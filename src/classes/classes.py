from pydantic import BaseModel, validator, root_validator
from typing import Optional
import MetaTrader5 as mt5
from enum import IntEnum, Enum, auto
from datetime import datetime
import pytz


class ENUM_TRADE_REQUEST_ACTIONS(IntEnum):
    """Trade actions

    Trading is done by sending orders to open positions using the OrderSend() function, as well as to place, modify or delete pending orders. Each trade order refers to the type of the requested operation.
        Trading operations are described in the ENUM_TRADE_REQUEST_ACTIONS enumeration.

    Args:
        TRADE_ACTION_DEAL (int): Place a trade order for an immediate execution with the specified parameters (market order). Default: 1
        TRADE_ACTION_PENDING (int): Place a trade order for the execution under specified conditions (pending order). Default: 5
        TRADE_ACTION_SLTP (int): Modify Stop Loss and Take Profit values of an opened position. Default: 6
        TRADE_ACTION_MODIFY (int): Modify the parameters of the order placed previously. Default: 7
        TRADE_ACTION_REMOVE (int): Delete the pending order placed previously. Default: 8
        TRADE_ACTION_CLOSE_BY (int): Close a position by an opposite one. Default: 10
    """

    TRADE_ACTION_DEAL: int = mt5.TRADE_ACTION_DEAL
    TRADE_ACTION_PENDING: int = mt5.TRADE_ACTION_PENDING
    TRADE_ACTION_SLTP: int = mt5.TRADE_ACTION_SLTP
    TRADE_ACTION_MODIFY: int = mt5.TRADE_ACTION_MODIFY
    TRADE_ACTION_REMOVE: int = mt5.TRADE_ACTION_REMOVE
    TRADE_ACTION_CLOSE_BY: int = mt5.TRADE_ACTION_CLOSE_BY


class ENUM_POSITION_TYPE(IntEnum):
    """Position types

    Direction of an open position (buy or sell)

    Args:
        POSITION_TYPE_BUY (int): Buy position.
        POSITION_TYPE_SELL (int): Sell position.
    """

    POSITION_TYPE_BUY: int = mt5.POSITION_TYPE_BUY
    POSITION_TYPE_SELL: int = mt5.POSITION_TYPE_SELL


class ENUM_POSITION_REASON(IntEnum):
    """Platform that the position was opened

    Args:
        POSITION_REASON_CLIENT (int): The position was opened as a result of activation of an order placed from a desktop terminal
        POSITION_REASON_EXPERT (int): The position was opened as a result of activation of an order placed from an MQL5 program, i.e. an Expert Advisor or a script
        POSITION_REASON_MOBILE (int): The position was opened as a result of activation of an order placed from a mobile application
        POSITION_REASON_WEB (int): The position was opened as a result of activation of an order placed from the web platform
    """

    POSITION_REASON_CLIENT: int = mt5.POSITION_REASON_CLIENT
    POSITION_REASON_EXPERT: int = mt5.POSITION_REASON_EXPERT
    POSITION_REASON_MOBILE: int = mt5.POSITION_REASON_MOBILE
    POSITION_REASON_WEB: int = mt5.POSITION_REASON_WEB


class ENUM_ORDER_TYPE(IntEnum):
    """Order types

    When sending a trade request using the OrderSend() function, some operations require the indication of the order type.
        The order type is specified in the type field of the special structure MqlTradeRequest, and can accept values of the ENUM_ORDER_TYPE enumeration.

    Args:
        ORDER_TYPE_BUY (int): Market Buy order. Default: 0
        ORDER_TYPE_SELL (int): Market Sell order. Default: 1
        ORDER_TYPE_BUY_LIMIT (int): Buy Limit pending order. Default: 2
        ORDER_TYPE_SELL_LIMIT (int): Sell Limit pending order. Default: 3
        ORDER_TYPE_BUY_STOP (int): Buy Stop pending order. Default: 4
        ORDER_TYPE_SELL_STOP (int): Sell Stop pending order. Default: 5
        ORDER_TYPE_BUY_STOP_LIMIT (int): Upon reaching the order price, a pending Buy Limit order is placed at the StopLimit price. Default: 6
        ORDER_TYPE_SELL_STOP_LIMIT (int): Upon reaching the order price, a pending Sell Limit order is placed at the StopLimit price. Default: 7
        ORDER_TYPE_CLOSE_BY (int): Order to close a position by an opposite one. Default: 8
    """

    ORDER_TYPE_BUY: int = mt5.ORDER_TYPE_BUY
    ORDER_TYPE_SELL: int = mt5.ORDER_TYPE_SELL
    ORDER_TYPE_BUY_LIMIT: int = mt5.ORDER_TYPE_BUY_LIMIT
    ORDER_TYPE_SELL_LIMIT: int = mt5.ORDER_TYPE_SELL_LIMIT
    ORDER_TYPE_BUY_STOP: int = mt5.ORDER_TYPE_BUY_STOP
    ORDER_TYPE_SELL_STOP: int = mt5.ORDER_TYPE_SELL_STOP
    ORDER_TYPE_BUY_STOP_LIMIT: int = mt5.ORDER_TYPE_BUY_STOP_LIMIT
    ORDER_TYPE_SELL_STOP_LIMIT: int = mt5.ORDER_TYPE_SELL_STOP_LIMIT
    ORDER_TYPE_CLOSE_BY: int = mt5.ORDER_TYPE_CLOSE_BY

    @classmethod
    def get_order_name(cls, name):
        return name.replace("ORDER_TYPE_", "")


class ENUM_ORDER_TYPE_MARKET(IntEnum):
    """Market order types

    Args:
        ORDER_TYPE_BUY (ENUM_ORDER_TYPE): Market Buy order.
        ORDER_TYPE_SELL (ENUM_ORDER_TYPE): Market Sell order.
    """

    ORDER_TYPE_BUY: ENUM_ORDER_TYPE = ENUM_ORDER_TYPE.ORDER_TYPE_BUY
    ORDER_TYPE_SELL: ENUM_ORDER_TYPE = ENUM_ORDER_TYPE.ORDER_TYPE_SELL


class ENUM_ORDER_TYPE_FILLING(IntEnum):
    """Volume filling policy

    Args:
        ORDER_FILLING_FOK (int): An order can be executed in the specified volume only.
        ORDER_FILLING_IOC (int): If the request cannot be filled completely, an order with the available volume will be executed, and the remaining volume will be canceled.
        ORDER_FILLING_BOC (int): The BoC order assumes that the order can only be placed in the Depth of Market and cannot be immediately executed. If the order can be executed immediately when placed, then it is canceled.
        ORDER_FILLING_RETURN (int): In case of partial filling, an order with remaining volume is not canceled but processed further.
    """

    ORDER_FILLING_FOK: int = mt5.ORDER_FILLING_FOK
    ORDER_FILLING_IOC: int = mt5.ORDER_FILLING_IOC
    ORDER_FILLING_BOC: int = mt5.ORDER_FILLING_BOC
    ORDER_FILLING_RETURN: int = mt5.ORDER_FILLING_RETURN


class ENUM_ORDER_TYPE_TIME(IntEnum):
    """Order validity period

    Args:
        ORDER_TIME_GTC (int): Good till cancel order
        ORDER_TIME_DAY (int): Good till current trade day order
        ORDER_TIME_SPECIFIED (int): Good till expired order
        ORDER_TIME_SPECIFIED_DAY (int): The order will be effective till 23:59:59 of the specified day.
    """

    ORDER_TIME_GTC: int = mt5.ORDER_TIME_GTC
    ORDER_TIME_DAY: int = mt5.ORDER_TIME_DAY
    ORDER_TIME_SPECIFIED: int = mt5.ORDER_TIME_SPECIFIED
    ORDER_TIME_SPECIFIED_DAY: int = mt5.ORDER_TIME_SPECIFIED_DAY


class ENUM_TRADE_RETCODE(IntEnum):
    """Order send result return codes

    Args:
        TRADE_RETCODE_REQUOTE (int): Requote. Default: 10004
        TRADE_RETCODE_REJECT (int): Request rejected. Default: 10006
        TRADE_RETCODE_CANCEL (int): Request canceled by trader. Default: 10007
        TRADE_RETCODE_PLACED (int): Order placed. Default: 10008
        TRADE_RETCODE_DONE (int): Request completed. Default: 10009
        TRADE_RETCODE_DONE_PARTIAL (int): Only part of the request was completed. Default: 10010
        TRADE_RETCODE_ERROR (int): Request processing error. Default: 10011
        TRADE_RETCODE_TIMEOUT (int): Request canceled by timeout. Default: 10012
        TRADE_RETCODE_INVALID (int): Invalid request. Default: 10013
        TRADE_RETCODE_INVALID_VOLUME (int): Invalid volume in the request. Default: 10014
        TRADE_RETCODE_INVALID_PRICE (int): Invalid price in the request. Default: 10015
        TRADE_RETCODE_INVALID_STOPS (int): Invalid stops in the request. Default: 10016
        TRADE_RETCODE_TRADE_DISABLED (int): Trade is disabled. Default: 10017
        TRADE_RETCODE_MARKET_CLOSED (int): Market is closed. Default: 10018
        TRADE_RETCODE_NO_MONEY (int): There is not enough money to complete the request. Default: 10019
        TRADE_RETCODE_PRICE_CHANGED (int): Prices changed. Default: 10020
        TRADE_RETCODE_PRICE_OFF (int): There are no quotes to process the request. Default: 10021
        TRADE_RETCODE_INVALID_EXPIRATION (int): Invalid order expiration date in the request. Default: 10022
        TRADE_RETCODE_ORDER_CHANGED (int): Order state changed. Default: 10023
        TRADE_RETCODE_TOO_MANY_REQUESTS (int): Too frequent requests. Default: 10024
        TRADE_RETCODE_NO_CHANGES (int): No changes in request. Default: 10025
        TRADE_RETCODE_SERVER_DISABLES_AT (int): Autotrading disabled by server. Default: 10026
        TRADE_RETCODE_CLIENT_DISABLES_AT (int): Autotrading disabled by client terminal. Default: 10027
        TRADE_RETCODE_LOCKED (int): Request locked for processing. Default: 10028
        TRADE_RETCODE_FROZEN (int): Order or position frozen. Default: 10029
        TRADE_RETCODE_INVALID_FILL (int): Invalid order filling type. Default: 10030
        TRADE_RETCODE_CONNECTION (int): No connection with the trade server. Default: 10031
        TRADE_RETCODE_ONLY_REAL (int): Operation is allowed only for live accounts. Default: 10032
        TRADE_RETCODE_LIMIT_ORDERS (int): The number of pending orders has reached the limit. Default: 10033
        TRADE_RETCODE_LIMIT_VOLUME (int): The volume of orders and positions for the symbol has reached the limit. Default: 10034
        TRADE_RETCODE_INVALID_ORDER (int): Incorrect or prohibited order type. Default: 10035
        TRADE_RETCODE_POSITION_CLOSED (int): Position with the specified POSITION_IDENTIFIER has already been closed. Default: 10036
        TRADE_RETCODE_INVALID_CLOSE_VOLUME (int): A close volume exceeds the current position volume. Default: 10038
        TRADE_RETCODE_CLOSE_ORDER_EXIST (int): A close order already exists for a specified position. This may happen when working in the hedging system:
            •when attempting to close a position with an opposite one, while close orders for the position already exist
            •when attempting to fully or partially close a position if the total volume of the already present close orders and the newly placed one exceeds the current position volume. Default: 10039
        TRADE_RETCODE_LIMIT_POSITIONS (int): The number of open positions simultaneously present on an account can be limited by the server settings. After a limit is reached, the server returns the TRADE_RETCODE_LIMIT_POSITIONS error when attempting to place an order. The limitation operates differently depending on the position accounting type:
            •Netting — number of open positions is considered. When a limit is reached, the platform does not let placing new orders whose execution may increase the number of open positions. In fact, the platform allows placing orders only for the symbols that already have open positions. The current pending orders are not considered since their execution may lead to changes in the current positions but it cannot increase their number.
            •Hedging — pending orders are considered together with open positions, since a pending order activation always leads to opening a new position. When a limit is reached, the platform does not allow placing both new market orders for opening positions and pending orders.. Default: 10040
        TRADE_RETCODE_REJECT_CANCEL (int): The pending order activation request is rejected, the order is canceled. Default: 10041
        TRADE_RETCODE_LONG_ONLY (int): The request is rejected, because the "Only long positions are allowed" rule is set for the symbol (POSITION_TYPE_BUY). Default: 10042
        TRADE_RETCODE_SHORT_ONLY (int): The request is rejected, because the "Only short positions are allowed" rule is set for the symbol (POSITION_TYPE_SELL). Default: 10043
        TRADE_RETCODE_CLOSE_ONLY (int): The request is rejected, because the "Only position closing is allowed" rule is set for the symbol . Default: 10044
        TRADE_RETCODE_FIFO_CLOSE (int): The request is rejected, because "Position closing is allowed only by FIFO rule" flag is set for the trading account (ACCOUNT_FIFO_CLOSE=true). Default: 10045
        TRADE_RETCODE_HEDGE_PROHIBITED (int): The request is rejected, because the "Opposite positions on a single symbol are disabled" rule is set for the trading account. For example, if the account has a Buy position, then a user cannot open a Sell position or place a pending sell order. The rule is only applied to accounts with hedging accounting system (ACCOUNT_MARGIN_MODE=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING).. Default: 10046
    """

    TRADE_RETCODE_REQUOTE: int = mt5.TRADE_RETCODE_REQUOTE
    TRADE_RETCODE_REJECT: int = mt5.TRADE_RETCODE_REJECT
    TRADE_RETCODE_CANCEL: int = mt5.TRADE_RETCODE_CANCEL
    TRADE_RETCODE_PLACED: int = mt5.TRADE_RETCODE_PLACED
    TRADE_RETCODE_DONE: int = mt5.TRADE_RETCODE_DONE
    TRADE_RETCODE_DONE_PARTIAL: int = mt5.TRADE_RETCODE_DONE_PARTIAL
    TRADE_RETCODE_ERROR: int = mt5.TRADE_RETCODE_ERROR
    TRADE_RETCODE_TIMEOUT: int = mt5.TRADE_RETCODE_TIMEOUT
    TRADE_RETCODE_INVALID: int = mt5.TRADE_RETCODE_INVALID
    TRADE_RETCODE_INVALID_VOLUME: int = mt5.TRADE_RETCODE_INVALID_VOLUME
    TRADE_RETCODE_INVALID_PRICE: int = mt5.TRADE_RETCODE_INVALID_PRICE
    TRADE_RETCODE_INVALID_STOPS: int = mt5.TRADE_RETCODE_INVALID_STOPS
    TRADE_RETCODE_TRADE_DISABLED: int = mt5.TRADE_RETCODE_TRADE_DISABLED
    TRADE_RETCODE_MARKET_CLOSED: int = mt5.TRADE_RETCODE_MARKET_CLOSED
    TRADE_RETCODE_NO_MONEY: int = mt5.TRADE_RETCODE_NO_MONEY
    TRADE_RETCODE_PRICE_CHANGED: int = mt5.TRADE_RETCODE_PRICE_CHANGED
    TRADE_RETCODE_PRICE_OFF: int = mt5.TRADE_RETCODE_PRICE_OFF
    TRADE_RETCODE_INVALID_EXPIRATION: int = mt5.TRADE_RETCODE_INVALID_EXPIRATION
    TRADE_RETCODE_ORDER_CHANGED: int = mt5.TRADE_RETCODE_ORDER_CHANGED
    TRADE_RETCODE_TOO_MANY_REQUESTS: int = mt5.TRADE_RETCODE_TOO_MANY_REQUESTS
    TRADE_RETCODE_NO_CHANGES: int = mt5.TRADE_RETCODE_NO_CHANGES
    TRADE_RETCODE_SERVER_DISABLES_AT: int = mt5.TRADE_RETCODE_SERVER_DISABLES_AT
    TRADE_RETCODE_CLIENT_DISABLES_AT: int = mt5.TRADE_RETCODE_CLIENT_DISABLES_AT
    TRADE_RETCODE_LOCKED: int = mt5.TRADE_RETCODE_LOCKED
    TRADE_RETCODE_FROZEN: int = mt5.TRADE_RETCODE_FROZEN
    TRADE_RETCODE_INVALID_FILL: int = mt5.TRADE_RETCODE_INVALID_FILL
    TRADE_RETCODE_CONNECTION: int = mt5.TRADE_RETCODE_CONNECTION
    TRADE_RETCODE_ONLY_REAL: int = mt5.TRADE_RETCODE_ONLY_REAL
    TRADE_RETCODE_LIMIT_ORDERS: int = mt5.TRADE_RETCODE_LIMIT_ORDERS
    TRADE_RETCODE_LIMIT_VOLUME: int = mt5.TRADE_RETCODE_LIMIT_VOLUME
    TRADE_RETCODE_INVALID_ORDER: int = mt5.TRADE_RETCODE_INVALID_ORDER
    TRADE_RETCODE_POSITION_CLOSED: int = mt5.TRADE_RETCODE_POSITION_CLOSED
    TRADE_RETCODE_INVALID_CLOSE_VOLUME: int = mt5.TRADE_RETCODE_INVALID_CLOSE_VOLUME
    TRADE_RETCODE_CLOSE_ORDER_EXIST: int = mt5.TRADE_RETCODE_CLOSE_ORDER_EXIST
    TRADE_RETCODE_LIMIT_POSITIONS: int = mt5.TRADE_RETCODE_LIMIT_POSITIONS
    TRADE_RETCODE_REJECT_CANCEL: int = mt5.TRADE_RETCODE_REJECT_CANCEL
    TRADE_RETCODE_LONG_ONLY: int = mt5.TRADE_RETCODE_LONG_ONLY
    TRADE_RETCODE_SHORT_ONLY: int = mt5.TRADE_RETCODE_SHORT_ONLY
    TRADE_RETCODE_CLOSE_ONLY: int = mt5.TRADE_RETCODE_CLOSE_ONLY
    TRADE_RETCODE_FIFO_CLOSE: int = mt5.TRADE_RETCODE_FIFO_CLOSE


class ENUM_CHECK_CODE(IntEnum):
    """Check return code

    Args:
        CHECK_RETCODE_OK (int): Successful request.
        CHECK_RETCODE_ERROR (int): Error request.
        CHECK_RETCODE_RETRY (int): Retry request.
    """

    CHECK_RETCODE_OK: int = auto()
    CHECK_RETCODE_ERROR: int = auto()
    CHECK_RETCODE_RETRY: int = auto()


class ENUM_ACCOUNT_TRADE_MODE(IntEnum):
    """Account Trade Mode

    Args:
        ACCOUNT_TRADE_MODE_DEMO (int): Demo account. Default: 0
        ACCOUNT_TRADE_MODE_CONTEST (int): Contest account. Default: 1
        ACCOUNT_TRADE_MODE_REAL (int): Real account. Default: 2
    """

    ACCOUNT_TRADE_MODE_DEMO: int = mt5.ACCOUNT_TRADE_MODE_DEMO
    ACCOUNT_TRADE_MODE_CONTEST: int = mt5.ACCOUNT_TRADE_MODE_CONTEST
    ACCOUNT_TRADE_MODE_REAL: int = mt5.ACCOUNT_TRADE_MODE_REAL


class ENUM_ACCOUNT_MARGIN_MODE(IntEnum):
    """Account Margin Mode

    Args:
        ACCOUNT_MARGIN_MODE_RETAIL_NETTING (int): Used for the exchange markets where individual positions aren't possible. Default: 0
        ACCOUNT_MARGIN_MODE_EXCHANGE (int): Used for the exchange markets. Default: 1
        ACCOUNT_MARGIN_MODE_RETAIL_HEDGING (int): Used for the exchange markets where individual positions are possible. Default: 2
    """

    ACCOUNT_MARGIN_MODE_RETAIL_NETTING: int = mt5.ACCOUNT_MARGIN_MODE_RETAIL_NETTING
    ACCOUNT_MARGIN_MODE_EXCHANGE: int = mt5.ACCOUNT_MARGIN_MODE_EXCHANGE
    ACCOUNT_MARGIN_MODE_RETAIL_HEDGING: int = mt5.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING


class ENUM_ACCOUNT_STOPOUT_MODE(IntEnum):
    """Account Margin Stop Out Mode

    Args:
        ACCOUNT_STOPOUT_MODE_PERCENT (int): Account stop out mode in percents. Default: 0
        ACCOUNT_STOPOUT_MODE_MONEY (int): Account stop out mode in money. Default: 1
    """

    ACCOUNT_STOPOUT_MODE_PERCENT: int = mt5.ACCOUNT_STOPOUT_MODE_PERCENT
    ACCOUNT_STOPOUT_MODE_MONEY: int = mt5.ACCOUNT_STOPOUT_MODE_MONEY


class MqlAccountInfo(BaseModel):
    """Account Info

    Args:
        login (int): Account login
        trade_mode (ENUM_ACCOUNT_TRADE_MODE): Account trade mode
        leverage (int): Account leverage
        limit_orders (int): Maximum allowed number of active pending orders
        margin_so_mode (ENUM_ACCOUNT_STOPOUT_MODE): Mode for setting the minimal allowed margin
        trade_allowed (bool): Allowed trade for the current account
        trade_expert (bool): Allowed trade for an Expert Advisor
        margin_mode (ENUM_ACCOUNT_TRADE_MODE): Margin calculation mode
        currency_digits (int): The number of decimal places in the account currency, which are required for an accurate display of trading results
        fifo_close (bool): An indication showing that positions can only be closed by FIFO rule.
            If the property value is set to true, then each symbol positions will be closed in the same order, in which they are opened, starting with the oldest one. In case of an attempt to close positions in a different order, the trader will receive an appropriate error.
        balance (float): Account balance in the deposit currency
        credit (float): Account credit in the deposit currency
        profit (float): Current profit of an account in the deposit currency
        equity (float): Account equity in the deposit currency
        margin (float): Account margin used in the deposit currency
        margin_free (float): Free margin of an account in the deposit currency
        margin_level (float): Account margin level in percents
        margin_so_call (float): Margin call level.
            Depending on the set ACCOUNT_MARGIN_SO_MODE is expressed in percents or in the deposit currency
        margin_so_so (float): Margin stop out level.
            Depending on the set ACCOUNT_MARGIN_SO_MODE is expressed in percents or in the deposit currency
        margin_initial (float): Initial margin.
            The amount reserved on an account to cover the margin of all pending orders
        margin_maintenance (float): Maintenance margin.
            The minimum equity reserved on an account to cover the minimum amount of all open positions
        assets (float): The current assets of an account
        liabilities (float): The current liabilities on an account
        commission_blocked (float): The current blocked commission amount on an account
        name (str): Client name
        server (str): Trade server name
        currency (str): Account currency
        company (str): Name of a company that serves the account
    """

    login: int
    trade_mode: ENUM_ACCOUNT_TRADE_MODE
    leverage: int
    limit_orders: int
    margin_so_mode: ENUM_ACCOUNT_STOPOUT_MODE
    trade_allowed: bool
    trade_expert: bool
    margin_mode: ENUM_ACCOUNT_MARGIN_MODE
    currency_digits: int
    fifo_close: bool
    balance: float
    credit: float
    profit: float
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    margin_so_call: float
    margin_so_so: float
    margin_initial: float
    margin_maintenance: float
    assets: float
    liabilities: float
    commission_blocked: float
    name: str
    server: str
    currency: str
    company: str

    @classmethod
    def parse_account(cls, account: mt5.AccountInfo) -> "MqlAccountInfo":
        """Parse a mt5.AccountInfo to MqlAccountInfo

        Args:
            account (mt5.AccountInfo): mt5 account object

        Raises:
            TypeError: Type not expected

        Returns:
            MqlAccountInfo: object declared
        """
        try:
            # Check object type
            if not isinstance(account, mt5.AccountInfo):
                raise TypeError

            dict_account = {
                "login": account.login,
                "trade_mode": account.trade_mode,
                "leverage": account.leverage,
                "limit_orders": account.limit_orders,
                "margin_so_mode": account.margin_so_mode,
                "trade_allowed": account.trade_allowed,
                "trade_expert": account.trade_expert,
                "margin_mode": account.margin_mode,
                "currency_digits": account.currency_digits,
                "fifo_close": account.fifo_close,
                "balance": account.balance,
                "credit": account.credit,
                "profit": account.profit,
                "equity": account.equity,
                "margin": account.margin,
                "margin_free": account.margin_free,
                "margin_level": account.margin_level,
                "margin_so_call": account.margin_so_call,
                "margin_so_so": account.margin_so_so,
                "margin_initial": account.margin_initial,
                "margin_maintenance": account.margin_maintenance,
                "assets": account.assets,
                "liabilities": account.liabilities,
                "commission_blocked": account.commission_blocked,
                "name": account.name,
                "server": account.server,
                "currency": account.currency,
                "company": account.company,
            }

        except (TypeError, ValueError) as e:
            raise TypeError(
                f"{cls.__name__} expected mt5.AccountInfo not {account.__class__.__name__}"
            )
        return cls(**dict_account)


class MqlTradeRequest(BaseModel):
    """Interaction between the client terminal and a trade server.

    Interaction between the client terminal and a trade server for executing the order placing operation is performed by using trade requests.

    Args:
        action (ENUM_TRADE_REQUEST_ACTIONS): Trade operation type
        symbol (str): Trade symbol
        magic (int): Expert Advisor ID (magic number).
        order (int): Order ticket.
        volume (float): Requested volume for a deal in lots
        price (float): Price
        stoplimit (float): StopLimit level of the order
        sl (float): Stop Loss level of the order
        tp (float): Take Profit level of the order
        deviation (int): Maximal possible deviation from the requested price. Default: 0
        type (ENUM_ORDER_TYPE): Order type
        type_filling (ENUM_ORDER_TYPE_FILLING): Order execution type
        type_time (EnumTradeRequestActions): Order expiration type
        expiration (EnumTradeRequestActions): Order expiration time (for the orders of ORDER_TIME_SPECIFIED type)
        comment (str): Order comment
        position (int): Position ticket
        position_by (int): The ticket of an opposite position

    Raises:
        ValidationError: magic, order, deviation, position, position_by
            must be equal or higher to zero
    """

    action: ENUM_TRADE_REQUEST_ACTIONS
    symbol: Optional[str] = None
    magic: Optional[int] = 0
    order: Optional[int] = None
    volume: Optional[float] = None
    price: Optional[float] = None
    stoplimit: Optional[float] = 0
    sl: Optional[float] = 0
    tp: Optional[float] = 0
    deviation: Optional[int] = 5
    type: Optional[ENUM_ORDER_TYPE] = None
    type_filling: Optional[
        ENUM_ORDER_TYPE_FILLING
    ] = ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_FOK
    type_time: Optional[ENUM_ORDER_TYPE_TIME] = ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC
    expiration: Optional[datetime] = None
    comment: Optional[str] = ""
    position: Optional[int] = None
    position_by: Optional[int] = None

    class Config:
        validate_assignment = True

    def prepare(self) -> dict:
        """Prepare request dict based on each trade action

        Returns:
            dict: Prepared request data
        """
        request = {}
        if self.action == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_DEAL:
            request.update(
                {
                    # Required Fields
                    "action": self.action,
                    "symbol": self.symbol,
                    "volume": self.volume,
                    "price": self.price,
                    "type": self.type,
                    # Optional fields
                    "deviation": self.deviation,
                    "type_filling": self.type_filling,
                }
            )

            if self.sl:
                request.update({"sl": self.sl})
            if self.tp:
                request.update({"tp": self.tp})
            if self.comment:
                request.update({"comment": self.comment})
            if self.magic:
                request.update({"magic": self.magic})

        elif self.action == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_PENDING:
            request.update(
                {
                    # Required Fields
                    "action": self.action,
                    "symbol": self.symbol,
                    "volume": self.volume,
                    "price": self.price,
                    "type": self.type,
                    # Optional fields
                    "type_filling": self.type_filling,
                    "deviation": self.deviation,
                    "type_time": self.type_time,
                }
            )

            if self.sl:
                request.update({"sl": self.sl})
            if self.tp:
                request.update({"tp": self.tp})
            if self.comment:
                request.update({"comment": self.comment})
            if self.magic:
                request.update({"magic": self.magic})

            # Set 'stoplimit'
            if self.type in [
                ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP_LIMIT,
                ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP_LIMIT,
            ]:
                request.update({"stoplimit": self.stoplimit})

            # Set 'expiration'
            if self.expiration:
                request.update({"expiration": int(self.expiration.timestamp())})

        elif self.action == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_SLTP:
            request.update(
                {
                    # Required Fields
                    "action": self.action,
                    "symbol": self.symbol,
                    "position": self.position,
                }
            )

            if self.sl:
                request.update({"sl": self.sl})
            if self.tp:
                request.update({"tp": self.tp})
            if self.comment:
                request.update({"comment": self.comment})
            if self.magic:
                request.update({"magic": self.magic})

        elif self.action == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_MODIFY:
            request.update(
                {
                    # Required Fields
                    "action": self.action,
                    "order": self.order,
                    "price": self.price,
                    # Optional Field
                    "type_time": self.type_time,
                }
            )

            if self.sl:
                request.update({"sl": self.sl})
            if self.tp:
                request.update({"tp": self.tp})
            if self.expiration:
                request.update({"expiration": int(self.expiration.timestamp())})

        elif self.action == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_REMOVE:
            request.update(
                {
                    # Required Fields
                    "action": self.action,
                    "order": self.order,
                    "type": self.type,
                }
            )

        elif self.action == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_CLOSE_BY:
            request.update(
                {
                    # Required Fields
                    "action": self.action,
                    "type": self.type,
                    "position": self.position,
                    "position_by": self.position_by,
                }
            )

        return request

    @classmethod
    def parse_request(cls, request: mt5.TradeRequest) -> "MqlTradeRequest":
        """Parse a mt5.TradeRequest to MqlTradeRequest

        Args:
            request (mt5.TradeRequest): mt5 request object

        Raises:
            TypeError: Type not expected

        Returns:
            MqlTradeRequest: object declared
        """
        try:
            # Check object type
            if not isinstance(request, mt5.TradeRequest):
                raise TypeError

            dict_request = {
                "action": request.action,
                "symbol": request.symbol,
                "magic": request.magic,
                "order": request.order,
                "volume": request.volume,
                "price": request.price,
                "stoplimit": request.stoplimit,
                "sl": request.sl,
                "tp": request.tp,
                "deviation": request.deviation,
                "type": request.type,
                "type_time": request.type_time,
                "type_filling": request.type_filling,
                "comment": request.comment,
                "position": request.position,
                "position_by": request.position_by,
            }
            if request.expiration:
                utc = pytz.timezone("UTC")
                expiration = utc.localize(datetime.utcfromtimestamp(request.expiration))
                dict_request.update({"expiration": expiration})

        except (TypeError, ValueError) as e:
            raise TypeError(
                f"{cls.__name__} expected mt5.TradeRequest not {request.__class__.__name__}"
            )
        return cls(**dict_request)

    @validator("expiration")
    def __validate_expiration(cls, value: datetime, values: dict):
        if value is not None and value.tzinfo is None:
            utc = pytz.timezone("UTC")
            value = utc.localize(value)

        return value

    @validator("magic", "order", "deviation", "position", "position_by")
    def __validate_fields_higher_than_zero(cls, value: int, values: dict) -> int:
        """Check for invalid negative numbers

        Args:
            value (int): Value to check
            values (dict): Class attributes

        Raises:
            ValueError: must be equal or higher to zero

        Returns:
            int: Validated value
        """
        # Check if the value is >= 0
        if value is not None and value < 0:
            raise ValueError("must be equal or higher to zero")

        return value

    @root_validator
    def __validate_tp_and_sl(cls, values: dict) -> dict:
        """Validate the stop loss and take profit positions

        Args:
            values (dict): class attributes

        Raises:
            ValueError: Invalid stop loss
            ValueError: Invalid take profit

        Returns:
            dict: class attributes
        """

        sl = values.get("sl", 0)
        tp = values.get("tp", 0)

        # Check if stop or take profit is defined
        if sl or tp:
            price = values.get("price", 0)
            stoplimit = values.get("stoplimit", 0)

            order_type = values.get("type")

            # Set buy order types
            buy_types = [
                ENUM_ORDER_TYPE.ORDER_TYPE_BUY,
                ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP,
                ENUM_ORDER_TYPE.ORDER_TYPE_BUY_LIMIT,
            ]

            # Set sell order types
            sell_types = [
                ENUM_ORDER_TYPE.ORDER_TYPE_SELL,
                ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP,
                ENUM_ORDER_TYPE.ORDER_TYPE_SELL_LIMIT,
            ]

            # Set stop-limit order types
            buy_stop_limit = ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP_LIMIT
            sell_stop_limit = ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP_LIMIT

            # Check the Stoploss position
            if sl and (
                # Invalid stop loss
                sl < 0
                # Buy orders
                or (order_type in buy_types and sl >= price)
                # Sell orders
                or (order_type in sell_types and sl <= price)
                # Buy stop limit
                or (order_type == buy_stop_limit and sl >= stoplimit)
                # Sell stop limit
                or (order_type == sell_stop_limit and sl <= stoplimit)
            ):
                raise ValueError("Invalid stop loss")
            # Check the Take Profit position
            if tp and (
                # Invalid take profit
                tp < 0
                # Buy orders
                or (order_type in buy_types and tp <= price)
                # Sell orders
                or (order_type in sell_types and tp >= price)
                # Buy stop limit
                or (order_type == buy_stop_limit and tp <= stoplimit)
                # Sell stop limit
                or (order_type == sell_stop_limit and tp >= stoplimit)
            ):
                raise ValueError("Invalid take profit")

        return values

    @root_validator
    def __validate_order_types(cls, values: dict) -> dict:
        """Validate the order type

        Args:
            values (dict): class attributes

        Raises:
            ValueError: Invalid order type

        Returns:
            dict: class attributes
        """

        action = values.get("action")
        order_type = values.get("type")

        # Check if stop or take profit is defined
        if order_type:
            # Market order
            market = [
                ENUM_ORDER_TYPE.ORDER_TYPE_BUY,
                ENUM_ORDER_TYPE.ORDER_TYPE_SELL,
            ]
            # Pending orders
            pending = [
                ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP,
                ENUM_ORDER_TYPE.ORDER_TYPE_BUY_LIMIT,
                ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP,
                ENUM_ORDER_TYPE.ORDER_TYPE_SELL_LIMIT,
                ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP_LIMIT,
                ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP_LIMIT,
            ]

            # close by order
            close_by = [ENUM_ORDER_TYPE.ORDER_TYPE_CLOSE_BY]

            if (
                # Market orders
                (
                    action == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_DEAL
                    and order_type not in market
                )
                # Pending orders
                or (
                    action == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_PENDING
                    and order_type not in pending
                )
                # Close by orders
                or (
                    action == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_CLOSE_BY
                    and order_type not in close_by
                )
            ):
                raise ValueError("Invalid order type")

        return values

    @root_validator
    def __validate_type_time(cls, values: dict) -> dict:
        """Validate type time

        Args:
            values (dict): class attributes

        Raises:
            ValueError: Invalid type time

        Returns:
            dict: class attributes
        """
        expiration = values.get("expiration")
        type_time = values.get("type_time")

        if (
            expiration
            and type_time
            not in [
                ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED,
                ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED_DAY,
            ]
        ) or (
            not expiration
            and type_time
            in [
                ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED,
                ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED_DAY,
            ]
        ):
            raise ValueError("Invalid type time")

        return values

    @root_validator
    def __validate_action_required_parameters(cls, values: dict) -> dict:
        """Check required fields for each action

        Args:
            values (dict): Class attributes

        Raises:
            ValueError: Errors on required fields

        Returns:
            dict: fields validated
        """

        error_list = []

        def validate_required_field(values: dict, field: str, error_list: list):
            if not values.get(field) and not issubclass(type(values.get(field)), Enum):
                error_list.append(f"The {field} is required.")

        # Action DEAL
        if values.get("action") == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_DEAL:
            # Check REQUIRED fields
            validate_required_field(values, "symbol", error_list)
            validate_required_field(values, "volume", error_list)
            validate_required_field(values, "price", error_list)
            validate_required_field(values, "type", error_list)

        # Action PENDING
        elif values.get("action") == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_PENDING:
            # Check REQUIRED fields
            validate_required_field(values, "symbol", error_list)
            validate_required_field(values, "volume", error_list)
            validate_required_field(values, "price", error_list)
            validate_required_field(values, "type", error_list)

        if values.get("action") == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_SLTP:
            validate_required_field(values, "symbol", error_list)
            validate_required_field(values, "position", error_list)

        if values.get("action") == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_MODIFY:
            validate_required_field(values, "order", error_list)
            validate_required_field(values, "price", error_list)

        if values.get("action") == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_REMOVE:
            validate_required_field(values, "order", error_list)

        if values.get("action") == ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_CLOSE_BY:
            validate_required_field(values, "type", error_list)
            validate_required_field(values, "position", error_list)
            validate_required_field(values, "position_by", error_list)

        if len(error_list):
            errors = "\n-".join(error_list)
            raise ValueError(f"The order type has the following errors: \n\n-{errors}")

        return values


class MqlTradeResult(BaseModel):
    """Result of a trade request

    A trade server returns data about the trade request processing result as a special predefined structure of MqlTradeResult type.

    Args:
        retcode (ENUM_TRADE_RETCODE): Operation return code
        deal (int): Deal ticket, if it is performed
        order (int): Order ticket, if it is placed
        volume (float): Deal volume, confirmed by broker
        price (float): Deal price, confirmed by broker
        bid (float): Current Bid price
        ask (float): Current Ask price
        comment (str): Broker comment to operation (by default it is filled by description of trade server return code)
        request_id (int): Request ID set by the terminal during the dispatch
        retcode_external (int): Return code of an external trading system
        request (MqlTradeRequest): The request that generate this result.
    """

    retcode: ENUM_TRADE_RETCODE
    deal: int
    order: int
    volume: float
    price: float
    bid: float
    ask: float
    comment: str
    request_id: int
    retcode_external: int
    request: Optional[MqlTradeRequest] = None

    class Config:
        validate_assignment = True

    @classmethod
    def parse_result(cls, result: mt5.OrderSendResult) -> "MqlTradeResult":
        """Parse a mt5.OrderSendResult object to MqlTradeResult

        Args:
            result (mt5.OrderSendResult): mt5 result object

        Raises:
            TypeError: Type not expected

        Returns:
            MqlTradeResult: object declared
        """
        try:
            # Check object type
            if not isinstance(result, mt5.OrderSendResult):
                raise TypeError

            dict_result = {
                "retcode": result.retcode,
                "deal": result.deal,
                "order": result.order,
                "volume": result.volume,
                "price": result.price,
                "bid": result.bid,
                "ask": result.ask,
                "comment": result.comment,
                "request_id": result.request_id,
                "retcode_external": result.retcode_external,
            }

            if result.request.action in ENUM_TRADE_REQUEST_ACTIONS.__members__.values():
                dict_result.update(
                    {
                        "request": MqlTradeRequest.parse_request(result.request),
                    }
                )

        except TypeError as e:
            raise TypeError(
                f"{cls.__name__} expected mt5.OrderSendResult not {result.__class__.__name__}"
            )
        return cls(**dict_result)


class MqlPositionInfo(BaseModel):
    """Position info

    Args:
        ticket (int): Unique number assigned to each newly opened position.
        time (int): Position open time
        time_msc (int): Position opening time in milliseconds since 01.01.1970
        time_update (int): Position changing time
        time_update_msc (int): Position changing time in milliseconds since 01.01.1970
        type (ENUM_POSITION_TYPE): Position type
        magic (int): Position magic number
        identifier (int): Position identifier is a unique number assigned to each re-opened position.
            It does not change throughout its life cycle and corresponds to the ticket of an order used to open a position.
        reason (ENUM_POSITION_REASON): The reason for opening a position
        volume (float): Position volume
        price_open (float): Position open price
        sl (float): Stop Loss level of opened position
        tp (float): Take Profit level of opened position
        price_current (float): Current price of the position symbol
        swap (float): Cumulative swap
        profit (float): Current profit
        symbol (str): Symbol of the position
        comment (str): Position comment
        external_id (str): Position identifier in an external trading system (on the Exchange)
    """

    ticket: int
    time: int
    time_msc: int
    time_update: int
    time_update_msc: int
    type: ENUM_POSITION_TYPE
    magic: int
    identifier: int
    reason: int
    volume: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    swap: float
    profit: float
    symbol: str
    comment: str
    external_id: str

    @classmethod
    def parse_position(cls, position: mt5.TradePosition) -> "MqlPositionInfo":
        """Parse a mt5.TradePosition to MqlPositionInfo

        Args:
            account (mt5.TradePosition): mt5 position object

        Raises:
            TypeError: Type not expected

        Returns:
            MqlPositionInfo: object declared
        """
        try:
            # Check object type
            if not isinstance(position, mt5.TradePosition):
                raise TypeError

            dict_position = {
                "ticket": position.ticket,
                "time": position.time,
                "time_msc": position.time_msc,
                "time_update": position.time_update,
                "time_update_msc": position.time_update_msc,
                "type": position.type,
                "magic": position.magic,
                "identifier": position.identifier,
                "reason": position.reason,
                "volume": position.volume,
                "price_open": position.price_open,
                "sl": position.sl,
                "tp": position.tp,
                "price_current": position.price_current,
                "swap": position.swap,
                "profit": position.profit,
                "symbol": position.symbol,
                "comment": position.comment,
                "external_id": position.external_id,
            }

        except (TypeError, ValueError) as e:
            raise TypeError(
                f"{cls.__name__} expected mt5.TradePosition not {position.__class__.__name__}"
            )
        return cls(**dict_position)
