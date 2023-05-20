import MetaTrader5 as mt5

from classes.classes import (
    MqlTradeRequest,
    MqlTradeResult,
    MqlAccountInfo,
    ENUM_ORDER_TYPE,
    ENUM_ORDER_TYPE_MARKET,
    ENUM_TRADE_REQUEST_ACTIONS,
    ENUM_ORDER_TYPE_FILLING,
    ENUM_TRADE_RETCODE,
    ENUM_CHECK_CODE,
    ENUM_ORDER_TYPE_TIME,
)
from datetime import datetime
import pytz
import time

MAX_RETRIES = 5  # Max retries on error
RETRY_DELAY = 0.5  # Retry delay in seconds


class Trade:
    """Trade utilility class"""

    def __init__(
        self,
        magic_number: int = None,
        deviation: int = 5,
        type_filling: ENUM_ORDER_TYPE_FILLING = ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_FOK,
    ) -> None:
        self.last_result: MqlTradeResult = None
        self.magic_number: int = magic_number
        self.deviation: int = deviation
        self.type_filling: int = type_filling

        # Set the account data attribute
        self.__refresh_account_info()

    def __refresh_account_info(self) -> None:
        """Refresg account attribute"""
        self.account: MqlAccountInfo = MqlAccountInfo.parse_account(mt5.account_info())

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
    def open_position(
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
            "type_filling": self.type_filling,
            "deviation": self.deviation,
            "magic": self.magic_number,
            "sl": stop_price,
            "tp": profit_price,
            "comment": comment,
        }

        request.update({"volume": volume})

        # Loop variables
        retry_count: int = 0
        check_code: ENUM_CHECK_CODE = ENUM_CHECK_CODE.CHECK_RETCODE_ERROR

        # Send request loop
        while retry_count <= MAX_RETRIES:
            # Get symbol tick
            symbol_tick: mt5.Tick = mt5.symbol_info_tick(symbol)

            # Get symbol price
            if order_type == ENUM_ORDER_TYPE_MARKET.ORDER_TYPE_BUY:
                request.update({"price": symbol_tick.ask})
            elif order_type == ENUM_ORDER_TYPE_MARKET.ORDER_TYPE_SELL:
                request.update({"price": symbol_tick.bid})

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

        # Update last result
        self.last_result = send_result

        return check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK

    def open_pending_order(
        self,
        symbol: str,
        order_type: ENUM_ORDER_TYPE_MARKET,
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

        # Update last result
        self.last_result = send_result

        return check_code == ENUM_CHECK_CODE.CHECK_RETCODE_OK

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
        success: bool = self.open_position(
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
        success: bool = self.open_position(
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
        success: bool = self.open_pending_order(
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
        success: bool = self.open_pending_order(
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
        success: bool = self.open_pending_order(
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
        success: bool = self.open_pending_order(
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
        success: bool = self.open_pending_order(
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
        success: bool = self.open_pending_order(
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
