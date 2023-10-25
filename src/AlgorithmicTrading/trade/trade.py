import MetaTrader5 as mt5
from datetime import datetime
from typing import Callable, List
import time
import pandas as pd

from AlgorithmicTrading.models.metatrader import (
    MqlTradeRequest,
    MqlTradeResult,
    MqlAccountInfo,
    MqlTradeOrder,
    MqlPositionInfo,
    MqlSymbolInfo,
    ENUM_ORDER_TYPE,
    ENUM_ORDER_TYPE_MARKET,
    ENUM_ORDER_TYPE_PENDING,
    ENUM_ORDER_TYPE_FILLING,
    ENUM_ORDER_TYPE_TIME,
    ENUM_TRADE_REQUEST_ACTIONS,
    ENUM_TRADE_RETCODE,
    ENUM_POSITION_TYPE,
    ENUM_CHECK_CODE,
)
from AlgorithmicTrading.account import AccountLive
from AlgorithmicTrading.rates import Rates
from AlgorithmicTrading.utils.metatrader import decorator_validate_mt5_connection
from AlgorithmicTrading.utils.trades import get_order
from AlgorithmicTrading.utils.exceptions import CouldNotSelectPosition
from AlgorithmicTrading.backtest.backtest import (
    decorator_backtest_open_position,
    decorator_backtest_open_pending_order,
    decorator_backtest_modify_position,
    decorator_backtest_modify_pending_order,
    decorator_backtest_close_position,
)

MAX_RETRIES = 5  # Max retries on error
RETRY_DELAY = 0.5  # Retry delay in seconds


class Trade:
    """Trade utilility class"""

    def __init__(
        self,
        account_data: MqlAccountInfo,
        magic_number: int = None,
        deviation: int = 5,
        type_filling: ENUM_ORDER_TYPE_FILLING = ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_FOK,
        backtest_env=None,
    ) -> None:
        self.account_data = account_data
        self.magic_number = magic_number
        self.deviation = deviation
        self.type_filling = type_filling
        self.backtest_env = backtest_env

    def __decorator_refresh_account_data(method: Callable) -> Callable:
        """Refresh account data

        Args:
            method (Callable): Server operation method

        Returns:
            Callable: Refresh function
        """

        # Refresh before and after
        def refresh_before_and_after(*args, **kwargs) -> Callable:
            """Refresh account data

            Refresh account data before and after the method execution

            Returns:
                Callable: original function
            """

            # Refresh the data
            def refresh_account_data(account: MqlAccountInfo) -> MqlAccountInfo:
                """Refresh account data

                Args:
                    account (MqlAccountInfo): Account

                Returns:
                    MqlAccountInfo: Refreshed data
                """
                # Check if the account is a backtest account
                if not account.is_backtest_account:
                    # Refresh account data
                    account: MqlAccountInfo = AccountLive.get_data()

                return account

            # Refresh before
            args[0].account_data = refresh_account_data(args[0].account_data)

            # Execute the method
            method_result: bool = method(*args, **kwargs)

            # Refresh after
            args[0].account_data = refresh_account_data(args[0].account_data)

            return method_result

        return refresh_before_and_after

    def __check_return_code(self, return_code: ENUM_TRADE_RETCODE) -> ENUM_CHECK_CODE:
        """Check how to deal with a request return code

        Args:
            return_code (ENUM_TRADE_RETCODE): Request return code

        Returns:
            ENUM_CHECK_CODE: How to deal with request
        """
        # Retries codes
        if return_code in (
            ENUM_TRADE_RETCODE.TRADE_RETCODE_REQUOTE,
            ENUM_TRADE_RETCODE.TRADE_RETCODE_CONNECTION,
            ENUM_TRADE_RETCODE.TRADE_RETCODE_PRICE_CHANGED,
            ENUM_TRADE_RETCODE.TRADE_RETCODE_TIMEOUT,
            ENUM_TRADE_RETCODE.TRADE_RETCODE_PRICE_OFF,
            ENUM_TRADE_RETCODE.TRADE_RETCODE_REJECT,
            ENUM_TRADE_RETCODE.TRADE_RETCODE_ERROR,
        ):
            status = ENUM_CHECK_CODE.CHECK_RETCODE_RETRY
        # Successfull codes
        elif return_code in (
            ENUM_TRADE_RETCODE.TRADE_RETCODE_DONE,
            ENUM_TRADE_RETCODE.TRADE_RETCODE_DONE_PARTIAL,
            ENUM_TRADE_RETCODE.TRADE_RETCODE_PLACED,
            ENUM_TRADE_RETCODE.TRADE_RETCODE_NO_CHANGES,
        ):
            status = ENUM_CHECK_CODE.CHECK_RETCODE_OK
        # Everything else is an error
        else:
            status = ENUM_CHECK_CODE.CHECK_RETCODE_ERROR

        return status

    # Open orders ---------------------------------------------------------------------
    @decorator_validate_mt5_connection
    @decorator_backtest_open_position
    @__decorator_refresh_account_data
    def __open_position(
        self,
        symbol: str,
        order_type: ENUM_ORDER_TYPE_MARKET,
        volume: float,
        stop_price: float = 0,
        profit_price: float = 0,
        comment: str = "",
    ) -> bool:
        """Open a market order

        Args:
            symbol (str): Trade symbol
            order_type (ENUM_MARKET_ORDER_TYPE): Market order type
            volume (float): Trade volume
            stop_price (float, optional): Trade stop price. Defaults to 0.
            profit_price (float, optional): Trade profit price. Defaults to 0.
            comment (str, optional): Trade comment. Defaults to "".

        Returns:
            bool: Check position opened
        """

        # Request data
        request = {
            # Required fields
            "action": ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "type": order_type,
            # Optional fields
            "sl": stop_price,
            "tp": profit_price,
            "comment": comment,
            "volume": volume,
            "type_filling": self.type_filling,
            "deviation": self.deviation,
            "magic": self.magic_number,
        }

        # Loop variables
        retry_count: int = 0
        check_code: ENUM_CHECK_CODE = ENUM_CHECK_CODE.CHECK_RETCODE_ERROR

        # Send request loop
        while retry_count <= MAX_RETRIES:
            # Get symbol data
            symbol_data: MqlSymbolInfo = Rates.get_symbol_data(symbol=symbol)

            # Get symbol price
            if order_type == ENUM_ORDER_TYPE_MARKET.ORDER_TYPE_BUY:
                request.update({"price": symbol_data.ask})
            elif order_type == ENUM_ORDER_TYPE_MARKET.ORDER_TYPE_SELL:
                request.update({"price": symbol_data.bid})

            # send a trading request
            prepared_request = MqlTradeRequest(**request).prepare()
            order_send = mt5.order_send(prepared_request)
            send_result = MqlTradeResult.parse_result(order_send)

            # Check the result
            check_code = self.__check_return_code(send_result.retcode)

            # OK - Exit the function
            if check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK:
                break
            # Error - Print the error
            elif check_code == ENUM_CHECK_CODE.CHECK_RETCODE_ERROR:
                print(
                    f"Open market order: Error {send_result.retcode} - {send_result.comment}"
                )
                break
            # Retry - Send the request again
            else:
                print("Server error detected, retrying...")
                time.sleep(RETRY_DELAY)
                retry_count += 1

        # Max retries reached
        if retry_count >= MAX_RETRIES:
            print(
                f"Max retries exceeded: Error {send_result.retcode} - {send_result.comment}"
            )

        # Order result
        print(
            f"Result: (Return Code) {send_result.retcode} - (Comment) {send_result.comment}",
            f"Order type: {ENUM_ORDER_TYPE.get_order_name(order_type.name)}",
            f"Order ticket: {send_result.order}",
            f"Symbol: {symbol}",
            f"Volume: {send_result.volume}",
            f"Price: {send_result.price}",
            f"Bid: {send_result.bid}",
            f"Ask: {send_result.ask}",
            sep="\n",
        )

        return check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK

    @decorator_validate_mt5_connection
    @decorator_backtest_open_pending_order
    @__decorator_refresh_account_data
    def __open_pending_order(
        self,
        symbol: str,
        order_type: ENUM_ORDER_TYPE_PENDING,
        volume: float,
        price: float,
        stop_limit: float = 0,
        stop_price: float = 0,
        profit_price: float = 0,
        expiration: datetime = None,
        comment: str = "",
    ) -> bool:
        """Open a pending order

        Args:
            symbol (str): Trade symbol
            order_type (ENUM_MARKET_ORDER_TYPE): Market order type
            volume (float): Trade volume
            stop_price (float, optional): Trade stop price. Defaults to 0.
            profit_price (float, optional): Trade profit price. Defaults to 0.
            comment (str, optional): Trade comment. Defaults to "".

        Returns:
            bool: Check position opened
        """

        # Request data
        request = {
            # Required fields
            "action": ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "type": order_type,
            "price": price,
            "volume": volume,
            # Optional fields
            "stoplimit": stop_limit,
            "sl": stop_price,
            "tp": profit_price,
            "comment": comment,
            "type_filling": self.type_filling,
            "deviation": self.deviation,
            "magic": self.magic_number,
        }

        if expiration:
            request.update({"expiration": expiration})
            request.update({"type_time": ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED})
        else:
            request.update({"type_time": ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC})

        # Loop variables
        retry_count: int = 0
        check_code: ENUM_CHECK_CODE = ENUM_CHECK_CODE.CHECK_RETCODE_ERROR

        # Send request loop
        while retry_count <= MAX_RETRIES:
            # send a trading request
            prepared_request = MqlTradeRequest(**request).prepare()
            order_send = mt5.order_send(prepared_request)
            send_result = MqlTradeResult.parse_result(order_send)

            # Check the result
            check_code = self.__check_return_code(send_result.retcode)

            # OK - Exit the function
            if check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK:
                break
            # Error - Print the error
            elif check_code == ENUM_CHECK_CODE.CHECK_RETCODE_ERROR:
                print(
                    f"Open pending order: Error {send_result.retcode} - {send_result.comment}"
                )
                break
            # Retry - Send the request again
            else:
                print("Server error detected, retrying...")
                time.sleep(RETRY_DELAY)
                retry_count += 1

        # Max retries reached
        if retry_count >= MAX_RETRIES:
            print(
                f"Max retries exceeded: Error {send_result.retcode} - {send_result.comment}"
            )

        # Order result
        print(
            f"Result: (Return Code) {send_result.retcode} - (Comment) {send_result.comment}",
            f"Order type: {ENUM_ORDER_TYPE.get_order_name(order_type.name)}",
            f"Order ticket: {send_result.order}",
            f"Symbol: {symbol}",
            f"Volume: {send_result.volume}",
            f"Price: {send_result.price}",
            f"Bid: {send_result.bid}",
            f"Ask: {send_result.ask}",
            sep="\n",
        )

        return check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK

    @decorator_validate_mt5_connection
    @decorator_backtest_modify_position
    @__decorator_refresh_account_data
    def modify_position(
        self,
        position_ticket: int = None,
        stop_price: float = None,
        profit_price: float = None,
        comment: str = "",
    ):
        position_not_found_error = CouldNotSelectPosition(
            "[ERROR]: Could not select the position."
        )

        if position_ticket is None:
            if len(self.account_data.positions) == 1:
                position_ticket = self.account_data.positions[0].ticket
            else:
                raise position_not_found_error

        # Get the position from account positions
        position_selected: List[MqlPositionInfo] = [
            mqlposition
            for mqlposition in self.account_data.positions
            if mqlposition.ticket == position_ticket
        ]

        # Check if the position exists
        if len(position_selected) != 1:
            raise position_not_found_error

        # Select the position object
        position_selected: MqlPositionInfo = position_selected[0]

        if position_selected.type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY:
            order_type = ENUM_ORDER_TYPE.ORDER_TYPE_BUY
        else:
            order_type = ENUM_ORDER_TYPE.ORDER_TYPE_SELL

        # Request data
        request = {
            # Required fields
            "action": ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_SLTP,
            "symbol": position_selected.symbol,
            "position": position_ticket,
            "price": position_selected.price_current,
            "type": order_type,
            # Optional fields
            "sl": stop_price,
            "tp": profit_price,
            "comment": comment,
            "magic": self.magic_number,
        }

        # Loop variables
        retry_count: int = 0
        check_code: ENUM_CHECK_CODE = ENUM_CHECK_CODE.CHECK_RETCODE_ERROR

        # Send request loop
        while retry_count <= MAX_RETRIES:
            # send a trading request
            prepared_request = MqlTradeRequest(**request).prepare()
            order_send = mt5.order_send(prepared_request)
            send_result = MqlTradeResult.parse_result(order_send)

            # Check the result
            check_code = self.__check_return_code(send_result.retcode)

            # OK - Exit the function
            if check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK:
                break
            # Error - Print the error
            elif check_code == ENUM_CHECK_CODE.CHECK_RETCODE_ERROR:
                print(
                    f"Modify position: Error {send_result.retcode} - {send_result.comment}"
                )
                break
            # Retry - Send the request again
            else:
                print("Server error detected, retrying...")
                time.sleep(RETRY_DELAY)
                retry_count += 1

        # Max retries reached
        if retry_count >= MAX_RETRIES:
            print(
                f"Max retries exceeded: Error {send_result.retcode} - {send_result.comment}"
            )

        # Order result
        print(
            f"Result: (Return Code) {send_result.retcode} - (Comment) {send_result.comment}",
            f"Order ticket: {send_result.order}",
            f"Volume: {send_result.volume}",
            f"Price: {send_result.price}",
            f"Bid: {send_result.bid}",
            f"Ask: {send_result.ask}",
            sep="\n",
        )

        return check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK

    @decorator_validate_mt5_connection
    @decorator_backtest_modify_pending_order
    @__decorator_refresh_account_data
    def modify_pending_order(
        self,
        ticket: int,
        price: float,
        stop_price: float = 0,
        profit_price: float = 0,
        expiration: datetime = None,
        comment: str = "",
    ):
        order: MqlTradeOrder = get_order(
            list_orders=self.account_data.orders, ticket=ticket
        )
        # Request data
        request = {
            # Required fields
            "action": ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_MODIFY,
            "order": ticket,
            "price": price,
            "type": order.type,
            # Optional fields
            "sl": stop_price,
            "tp": profit_price,
            "comment": comment,
            "type_filling": self.type_filling,
            "deviation": self.deviation,
            "magic": self.magic_number,
        }

        if expiration:
            request.update({"expiration": expiration})
            request.update({"type_time": ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED})
        else:
            request.update({"type_time": ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC})

        # Loop variables
        retry_count: int = 0
        check_code: ENUM_CHECK_CODE = ENUM_CHECK_CODE.CHECK_RETCODE_ERROR

        # Send request loop
        while retry_count <= MAX_RETRIES:
            # send a trading request
            prepared_request = MqlTradeRequest(**request).prepare()
            order_send = mt5.order_send(prepared_request)
            send_result = MqlTradeResult.parse_result(order_send)

            # Check the result
            check_code = self.__check_return_code(send_result.retcode)

            # OK - Exit the function
            if check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK:
                break
            # Error - Print the error
            elif check_code == ENUM_CHECK_CODE.CHECK_RETCODE_ERROR:
                print(
                    f"Modify pending order: Error {send_result.retcode} - {send_result.comment}"
                )
                break
            # Retry - Send the request again
            else:
                print("Server error detected, retrying...")
                time.sleep(RETRY_DELAY)
                retry_count += 1

        # Max retries reached
        if retry_count >= MAX_RETRIES:
            print(
                f"Max retries exceeded: Error {send_result.retcode} - {send_result.comment}"
            )

        # Order result
        print(
            f"Result: (Return Code) {send_result.retcode} - (Comment) {send_result.comment}",
            f"Order ticket: {send_result.order}",
            f"Volume: {send_result.volume}",
            f"Price: {send_result.price}",
            f"Bid: {send_result.bid}",
            f"Ask: {send_result.ask}",
            sep="\n",
        )

        return check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK

    @decorator_validate_mt5_connection
    @decorator_backtest_close_position
    @__decorator_refresh_account_data
    def close_position(self, position_ticket: int, comment: str = ""):
        position_not_found_error = CouldNotSelectPosition(
            "[ERROR]: Could not select the position."
        )

        # Get the position from account positions
        position_selected: List[MqlPositionInfo] = [
            mqlposition
            for mqlposition in self.account_data.positions
            if mqlposition.ticket == position_ticket
        ]

        # Check if the position exists
        if len(position_selected) != 1:
            raise position_not_found_error

        # Select the position object
        position_selected: MqlPositionInfo = position_selected[0]

        # Get symbol tick
        symbol_data: MqlSymbolInfo = Rates.get_symbol_data(
            symbol=position_selected.symbol
        )

        # Get the oposite direction type and price
        if position_selected.type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY:
            order_type = ENUM_ORDER_TYPE.ORDER_TYPE_SELL
            price = symbol_data.bid
        else:
            order_type = ENUM_ORDER_TYPE.ORDER_TYPE_BUY
            price = symbol_data.ask

        # Request data
        request = {
            # Required fields
            "action": ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_DEAL,
            "symbol": position_selected.symbol,
            "volume": position_selected.volume,
            "type": order_type,
            "position": position_ticket,
            "price": price,
            # Optional fields
            "comment": comment,
            "magic": self.magic_number,
            "type_time": ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC,
            "type_filling": ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_RETURN,
        }

        # Loop variables
        retry_count: int = 0
        check_code: ENUM_CHECK_CODE = ENUM_CHECK_CODE.CHECK_RETCODE_ERROR

        # Send request loop
        while retry_count <= MAX_RETRIES:
            # send a trading request
            prepared_request = MqlTradeRequest(**request).prepare()
            order_send = mt5.order_send(prepared_request)
            send_result = MqlTradeResult.parse_result(order_send)

            # Check the result
            check_code = self.__check_return_code(send_result.retcode)

            # OK - Exit the function
            if check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK:
                break
            # Error - Print the error
            elif check_code == ENUM_CHECK_CODE.CHECK_RETCODE_ERROR:
                print(
                    f"Close position: Error {send_result.retcode} - {send_result.comment}"
                )
                break
            # Retry - Send the request again
            else:
                print("Server error detected, retrying...")
                time.sleep(RETRY_DELAY)
                retry_count += 1

        # Max retries reached
        if retry_count >= MAX_RETRIES:
            print(
                f"Max retries exceeded: Error {send_result.retcode} - {send_result.comment}"
            )

        # Order result
        print(
            f"Result: (Return Code) {send_result.retcode} - (Comment) {send_result.comment}",
            f"Order ticket: {send_result.order}",
            f"Volume: {send_result.volume}",
            f"Price: {send_result.price}",
            f"Bid: {send_result.bid}",
            f"Ask: {send_result.ask}",
            sep="\n",
        )

        return check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK

    def close_all_positions(self, comment=""):
        for position in self.account_data.positions:
            self.close_position(position_ticket=position.ticket, comment=comment)

    # Market trade open shortcuts -----------------------------------------------------
    def buy(
        self,
        symbol: str,
        volume: float,
        stop_price: float = 0,
        profit_price: float = 0,
        comment: str = "",
    ) -> bool:
        """Open a buy market order

        Args:
            symbol (str): Trade symbol
            volume (float): Trade volume
            stop_price (float, optional): Trade stop price. Defaults to 0.
            profit_price (float, optional): Trade profit price. Defaults to 0.
            comment (str, optional): Trade comment. Defaults to "".

        Returns:
            bool: Check position opened
        """
        success: bool = self.__open_position(
            symbol=symbol,
            volume=volume,
            stop_price=stop_price,
            profit_price=profit_price,
            comment=comment,
            order_type=ENUM_ORDER_TYPE_MARKET.ORDER_TYPE_BUY,
        )
        return success

    def sell(
        self,
        symbol: str,
        volume: float,
        stop_price: float = 0,
        profit_price: float = 0,
        comment: str = "",
    ) -> bool:
        """Open a sell market order

        Args:
            symbol (str): Trade symbol
            volume (float): Trade volume
            stop_price (float, optional): Trade stop price. Defaults to 0.
            profit_price (float, optional): Trade profit price. Defaults to 0.
            comment (str, optional): Trade comment. Defaults to "".

        Returns:
            bool: Check position opened
        """
        success: bool = self.__open_position(
            symbol=symbol,
            volume=volume,
            stop_price=stop_price,
            profit_price=profit_price,
            comment=comment,
            order_type=ENUM_ORDER_TYPE_MARKET.ORDER_TYPE_SELL,
        )
        return success

    # Pending trade open shortcuts ----------------------------------------------------
    # Buy orders
    def buy_stop(
        self,
        symbol: str,
        volume: float,
        price: float,
        stop_price: float = 0,
        profit_price: float = 0,
        expiration: datetime = None,
        comment: str = "",
    ) -> bool:
        """Open a buy stop order

        Args:
            symbol (str): Trade symbol
            volume (float): Trade volume
            price (float): Trade price
            stop_price (float, optional): Trade stop price. Defaults to 0.
            profit_price (float, optional): Trade profit price. Defaults to 0.
            expiration (datetime, optional): Order expiration. Defaults to None.
            comment (str, optional): Trade comment. Defaults to "".

        Returns:
            bool: Check position opened
        """
        success: bool = self.__open_pending_order(
            symbol=symbol,
            volume=volume,
            price=price,
            stop_price=stop_price,
            profit_price=profit_price,
            expiration=expiration,
            comment=comment,
            order_type=ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP,
        )
        return success

    def buy_limit(
        self,
        symbol: str,
        volume: float,
        price: float,
        stop_price: float = 0,
        profit_price: float = 0,
        expiration: datetime = None,
        comment: str = "",
    ) -> bool:
        """Open a buy limit order

        Args:
            symbol (str): Trade symbol
            volume (float): Trade volume
            price (float): Trade price
            stop_price (float, optional): Trade stop price. Defaults to 0.
            profit_price (float, optional): Trade profit price. Defaults to 0.
            expiration (datetime, optional): Order expiration. Defaults to None.
            comment (str, optional): Trade comment. Defaults to "".

        Returns:
            bool: Check position opened
        """
        success: bool = self.__open_pending_order(
            symbol=symbol,
            volume=volume,
            price=price,
            stop_price=stop_price,
            profit_price=profit_price,
            expiration=expiration,
            comment=comment,
            order_type=ENUM_ORDER_TYPE.ORDER_TYPE_BUY_LIMIT,
        )
        return success

    def buy_stop_limit(
        self,
        symbol: str,
        volume: float,
        price: float,
        stop_limit: float,
        stop_price: float = 0,
        profit_price: float = 0,
        expiration: datetime = None,
        comment: str = "",
    ) -> bool:
        """Open a buy stop limit order

        Args:
            symbol (str): Trade symbol
            volume (float): Trade volume
            price (float): Trade price
            stop_limit (float): Trade stop limit price
            stop_price (float, optional): Trade stop price. Defaults to 0.
            profit_price (float, optional): Trade profit price. Defaults to 0.
            expiration (datetime, optional): Order expiration. Defaults to None.
            comment (str, optional): Trade comment. Defaults to "".

        Returns:
            bool: Check position opened
        """
        success: bool = self.__open_pending_order(
            symbol=symbol,
            volume=volume,
            price=price,
            stop_limit=stop_limit,
            stop_price=stop_price,
            profit_price=profit_price,
            expiration=expiration,
            comment=comment,
            order_type=ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP_LIMIT,
        )
        return success

    # Sell orders
    def sell_limit(
        self,
        symbol: str,
        volume: float,
        price: float,
        stop_price: float = 0,
        profit_price: float = 0,
        expiration: datetime = None,
        comment: str = "",
    ) -> bool:
        """Open a sell limit order

        Args:
            symbol (str): Trade symbol
            volume (float): Trade volume
            price (float): Trade price
            stop_price (float, optional): Trade stop price. Defaults to 0.
            profit_price (float, optional): Trade profit price. Defaults to 0.
            expiration (datetime, optional): Order expiration. Defaults to None.
            comment (str, optional): Trade comment. Defaults to "".

        Returns:
            bool: Check position opened
        """
        success: bool = self.__open_pending_order(
            symbol=symbol,
            volume=volume,
            price=price,
            stop_price=stop_price,
            profit_price=profit_price,
            expiration=expiration,
            comment=comment,
            order_type=ENUM_ORDER_TYPE.ORDER_TYPE_SELL_LIMIT,
        )
        return success

    def sell_stop(
        self,
        symbol: str,
        volume: float,
        price: float,
        stop_price: float = 0,
        profit_price: float = 0,
        expiration: datetime = None,
        comment: str = "",
    ) -> bool:
        """Open a sell stop order

        Args:
            symbol (str): Trade symbol
            volume (float): Trade volume
            price (float): Trade price
            stop_price (float, optional): Trade stop price. Defaults to 0.
            profit_price (float, optional): Trade profit price. Defaults to 0.
            expiration (datetime, optional): Order expiration. Defaults to None.
            comment (str, optional): Trade comment. Defaults to "".

        Returns:
            bool: Check position opened
        """
        success: bool = self.__open_pending_order(
            symbol=symbol,
            volume=volume,
            price=price,
            stop_price=stop_price,
            profit_price=profit_price,
            expiration=expiration,
            comment=comment,
            order_type=ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP,
        )
        return success

    def sell_stop_limit(
        self,
        symbol: str,
        volume: float,
        price: float,
        stop_limit: float,
        stop_price: float = 0,
        profit_price: float = 0,
        expiration: datetime = None,
        comment: str = "",
    ) -> bool:
        """Open a sell stop limit order

        Args:
            symbol (str): Trade symbol
            volume (float): Trade volume
            price (float): Trade price
            stop_limit (float): Trade stop limit price
            stop_price (float, optional): Trade stop price. Defaults to 0.
            profit_price (float, optional): Trade profit price. Defaults to 0.
            expiration (datetime, optional): Order expiration. Defaults to None.
            comment (str, optional): Trade comment. Defaults to "".

        Returns:
            bool: Check position opened
        """
        success: bool = self.__open_pending_order(
            symbol=symbol,
            volume=volume,
            price=price,
            stop_limit=stop_limit,
            stop_price=stop_price,
            profit_price=profit_price,
            expiration=expiration,
            comment=comment,
            order_type=ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP_LIMIT,
        )
        return success
