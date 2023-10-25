from typing import Callable
from datetime import datetime, timezone
from AlgorithmicTrading.models.metatrader import (
    MqlPositionInfo,
    MqlTradeDeal,
    MqlSymbolInfo,
    MqlTick,
    MqlTradeOrder,
    ENUM_ACCOUNT_MARGIN_MODE,
    ENUM_DEAL_TYPE,
    ENUM_DEAL_ENTRY,
    ENUM_DEAL_REASON,
    ENUM_ORDER_TYPE,
    ENUM_ORDER_REASON,
    ENUM_ORDER_TYPE_MARKET,
    ENUM_ORDER_TYPE_PENDING,
    ENUM_ORDER_STATE,
    ENUM_POSITION_REASON,
    ENUM_POSITION_TYPE,
    ENUM_ORDER_TYPE_TIME,
)
from AlgorithmicTrading.rates import Rates
from AlgorithmicTrading.utils.dates import get_timestamp_ms
from AlgorithmicTrading.utils.trades import (
    compute_profit,
    get_last_tick,
    get_order,
)
from AlgorithmicTrading.utils.exceptions import CouldNotSelectPosition
from typing import Any, List


def __get_deal_type(
    order_type: ENUM_ORDER_TYPE,
) -> ENUM_DEAL_TYPE:
    """Get deal type

    Args:
        order_type (ENUM_ORDER_TYPE): Order type

    Raises:
        TypeError: Invalid order type

    Returns:
        ENUM_DEAL_TYPE: Deal type
    """
    if order_type in (
        ENUM_ORDER_TYPE.ORDER_TYPE_BUY,
        ENUM_ORDER_TYPE.ORDER_TYPE_BUY_LIMIT,
        ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP,
        ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP_LIMIT,
    ):
        return ENUM_DEAL_TYPE.DEAL_TYPE_BUY

    if order_type in (
        ENUM_ORDER_TYPE.ORDER_TYPE_SELL,
        ENUM_ORDER_TYPE.ORDER_TYPE_SELL_LIMIT,
        ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP,
        ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP_LIMIT,
    ):
        return ENUM_DEAL_TYPE.DEAL_TYPE_SELL

    raise TypeError("[ERROR]: Invalid order type")


def __get_entry(
    volume: float,
    order_type: ENUM_ORDER_TYPE,
    position: MqlPositionInfo,
) -> ENUM_DEAL_ENTRY:
    """Get deal entry

    Args:
        volume (float): Deal volume
        order_type (ENUM_ORDER_TYPE): Order type
        position (MqlPositionInfo): Position opened

    Returns:
        ENUM_DEAL_ENTRY: Deal entry
    """
    # Oposite order direction
    if (
        position.type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY
        and order_type
        in (
            ENUM_ORDER_TYPE.ORDER_TYPE_SELL,
            ENUM_ORDER_TYPE.ORDER_TYPE_SELL_LIMIT,
            ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP,
            ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP_LIMIT,
        )
    ) or (
        position.type == ENUM_POSITION_TYPE.POSITION_TYPE_SELL
        and order_type
        in (
            ENUM_ORDER_TYPE.ORDER_TYPE_BUY,
            ENUM_ORDER_TYPE.ORDER_TYPE_BUY_LIMIT,
            ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP,
            ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP_LIMIT,
        )
    ):
        # Close position
        if volume <= position.volume:
            return ENUM_DEAL_ENTRY.DEAL_ENTRY_OUT

        # Revert position
        return ENUM_DEAL_ENTRY.DEAL_ENTRY_INOUT

    return ENUM_DEAL_ENTRY.DEAL_ENTRY_IN


def __backtest_get_profit(
    symbol: str,
    price_open: float,
    price_close: float,
    price_volume: float,
    last_tick: MqlTick,
    position_type: ENUM_POSITION_TYPE,
    position_entry: ENUM_DEAL_ENTRY,
    account_currency: str,
) -> float:
    """Get the profit of a backtest position

    Args:
        symbol (str): Symbol pair
        price_open (float): Price where position was openned
        price_close (float): Price where position is being closed
        price_volume (float): Volume closing
        last_tick (MqlTick): Last tick on candlestick chart at current step
        position_type (ENUM_POSITION_TYPE): Position type
        account_currency (str): Currency of account

    Returns:
        float: Position profit
    """

    # Get symbol information
    symbol_data: MqlSymbolInfo = Rates.get_symbol_data(symbol)

    # Compute profit
    profit: float = compute_profit(
        position_type=position_type,
        price_open=price_open,
        price_close=price_close,
        price_volume=price_volume,
        tick_close=last_tick,
        symbol_data=symbol_data,
        account_currency=account_currency,
    )

    return profit


def __backtest_create_a_deal(
    symbol: str,
    deal_time: datetime,
    order_type: ENUM_ORDER_TYPE,
    volume: float,
    price: float,
    position: MqlPositionInfo,
    trade_class: Any,
    fee: float = 0,
    commission: float = 0,
    order: int = None,
    comment: str = "",
) -> MqlTradeDeal:
    """Create a deal on backtest account

    Args:
        symbol (str): Symbol pair
        deal_time (datetime): Deal time
        order_type (ENUM_ORDER_TYPE): Order type
        volume (float): Order volume
        price (float): Order price
        position (MqlPositionInfo): Position openned
        trade_class (Any): Trade class received on decorator
        fee (float, optional): Order fee. Defaults to 0.
        commission (float, optional): Order comission. Defaults to 0.
        order (int, optional): Order identification. Defaults to None.
        comment (str, optional): Comment. Defaults to "".

    Returns:
        MqlTradeDeal: Prepared deal
    """

    # Generate a deal ticket
    random_ticket = get_timestamp_ms(deal_time)

    # Get order ID
    order_id = (
        order if order is not None else get_timestamp_ms(datetime.now(timezone.utc))
    )

    # Get deal type
    deal_type = __get_deal_type(order_type=order_type)

    # Get entry in or out
    entry = __get_entry(
        order_type=order_type,
        volume=volume,
        position=position,
    )

    # Get deal profit
    if entry != ENUM_DEAL_ENTRY.DEAL_ENTRY_IN:
        # Get last candle tick on the current step
        last_tick = get_last_tick(
            symbol,
            trade_class.backtest_env.df.iloc[
                : trade_class.backtest_env.current_step + 1
            ],
        )

        # Get volume of a partial out or full out deal
        close_volume = (
            volume if entry != ENUM_DEAL_ENTRY.DEAL_ENTRY_INOUT else position.volume
        )

        # Get profit of last tick
        profit = __backtest_get_profit(
            symbol=symbol,
            account_currency=trade_class.account_data.currency,
            position_type=position.type,
            price_open=position.price_open,
            price_close=price,
            price_volume=close_volume,
            last_tick=last_tick,
            position_entry=entry,
        )
    else:
        # Deals with entry In does not have profit
        profit = 0

    deal = MqlTradeDeal(
        symbol=symbol,
        ticket=random_ticket,
        order=order_id,
        time=deal_time.replace(microsecond=0),
        time_msc=deal_time,
        type=deal_type,
        entry=entry,
        position_id=position.ticket,
        volume=volume,
        price=price,
        commission=commission,
        swap=0,
        profit=profit,
        fee=fee,
        comment=comment,
        magic=trade_class.magic_number,
        reason=ENUM_DEAL_REASON.DEAL_REASON_EXPERT,
        external_id=None,
    )

    return deal


def __backtest_open_position(
    trade_class: Any,
    symbol: str,
    order_type: ENUM_ORDER_TYPE_MARKET,
    volume: float,
    stop_price: float = 0,
    profit_price: float = 0,
    commission: float = 0,
    fee: float = 0,
    comment: str = "",
) -> bool:
    """Open a position in backtest account

    Args:
        trade_class (Any): Trade class received by decorator
        symbol (str): Symbol pair
        order_type (ENUM_ORDER_TYPE_MARKET): Market order type
        volume (float): Order Volume
        stop_price (float, optional): Stop price. Defaults to 0.
        profit_price (float, optional): Take profit price. Defaults to 0.
        commission (float, optional): Commission. Defaults to 0.
        fee (float, optional): Fee. Defaults to 0.
        comment (str, optional): Comment. Defaults to "".

    Returns:
        bool: True, the same as a sucessful order in live trading
    """

    # Get last tick of candle on current step
    last_tick = get_last_tick(
        symbol,
        trade_class.backtest_env.df.iloc[: trade_class.backtest_env.current_step + 1],
    )

    # Get last tick time as position time
    position_time = last_tick.time
    position_time_ms = get_timestamp_ms(position_time)

    # Select price based on position type
    if order_type == ENUM_ORDER_TYPE_MARKET.ORDER_TYPE_BUY:
        price = last_tick.ask
    else:
        price = last_tick.bid

    # Convert market position type to standard position type
    position_type = ENUM_POSITION_TYPE(order_type)

    # Create a position object
    position = MqlPositionInfo(
        ticket=get_timestamp_ms(datetime.now(tz=timezone.utc)),
        time=position_time,
        time_msc=position_time,
        time_update=position_time,
        time_update_msc=position_time,
        type=position_type,
        magic=trade_class.magic_number,
        identifier=position_time_ms,
        reason=ENUM_POSITION_REASON.POSITION_REASON_EXPERT,
        volume=volume,
        price_open=price,
        price_current=price,
        sl=stop_price,
        tp=profit_price,
        swap=0,
        profit=0,
        symbol=symbol,
        comment=comment,
        external_id=None,
    )

    # Hedge account
    if (
        trade_class.account_data
        == ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING
    ):
        deal = __backtest_create_a_deal(
            position=position,
            deal_time=position.time,
            symbol=symbol,
            order_type=order_type,
            volume=volume,
            price=position.price_current,
            trade_class=trade_class,
            fee=fee,
            commission=commission,
            order=None,
            comment=comment,
        )
        trade_class.account_data.positions.append(position)
        trade_class.account_data.history_deals.append(deal)
    # Netting account
    else:
        # Check if there is a position already opened
        if trade_class.account_data.positions:
            opened_position = trade_class.account_data.positions[0]

            position.identifier = opened_position.identifier
            position.volume = opened_position.volume
            position.type = opened_position.type

            # Check if there is a position on the other direction
            if opened_position.type != position_type:
                # Equal volumes
                if opened_position.volume == volume:
                    deal = __backtest_create_a_deal(
                        deal_time=position.time,
                        position=position,
                        symbol=symbol,
                        order_type=order_type,
                        volume=volume,
                        price=position.price_current,
                        trade_class=trade_class,
                        fee=fee,
                        commission=commission,
                        order=None,
                        comment=comment,
                    )

                    trade_class.account_data.history_deals.append(deal)

                    # Close position
                    del trade_class.account_data.positions[0]

                # Higher volume - Keep direction
                elif opened_position.volume > volume:
                    deal = __backtest_create_a_deal(
                        deal_time=position.time,
                        position=position,
                        symbol=symbol,
                        order_type=order_type,
                        volume=volume,
                        price=position.price_current,
                        trade_class=trade_class,
                        fee=fee,
                        commission=commission,
                        order=None,
                        comment=comment,
                    )

                    position.volume = round(position.volume - volume, 2)

                    trade_class.account_data.positions[0] = position
                    trade_class.account_data.history_deals.append(deal)

                # Lower volume - Revert
                elif opened_position.volume < volume:
                    # Change the identifier
                    position.identifier = position_time_ms

                    # Close the opened direction position
                    deal_close = __backtest_create_a_deal(
                        deal_time=position.time,
                        position=opened_position,
                        symbol=symbol,
                        order_type=order_type,
                        volume=volume,
                        price=position.price_current,
                        trade_class=trade_class,
                        fee=fee,
                        commission=commission,
                        order=None,
                        comment=comment,
                    )

                    # Get new volume
                    position.volume = round(abs(position.volume - volume), 2)

                    # Change the position type
                    if position.type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY:
                        position.type = ENUM_POSITION_TYPE.POSITION_TYPE_SELL
                    else:
                        position.type = ENUM_POSITION_TYPE.POSITION_TYPE_BUY

                    # Set a new position price open
                    position.price_open = position.price_current

                    trade_class.account_data.positions[0] = position
                    trade_class.account_data.history_deals.append(deal_close)

            # Check if there is a position on the same direction
            else:
                deal = __backtest_create_a_deal(
                    deal_time=position.time,
                    position=position,
                    symbol=symbol,
                    order_type=order_type,
                    volume=volume,
                    price=position.price_current,
                    trade_class=trade_class,
                    fee=fee,
                    commission=commission,
                    order=None,
                    comment=comment,
                )

                # Compute a new volume and price
                total_volume = round(position.volume + volume, 2)
                mean_price = (
                    (opened_position.price_open * opened_position.volume)
                    + (position.price_open * volume)
                ) / total_volume
                position.volume = total_volume
                position.price_open = mean_price
                position.price_current = mean_price

                # Replace position
                trade_class.account_data.positions[0] = position

                trade_class.account_data.history_deals.append(deal)

        # No positions opened
        else:
            deal = __backtest_create_a_deal(
                deal_time=position.time,
                position=position,
                symbol=symbol,
                order_type=order_type,
                volume=volume,
                price=position.price_current,
                trade_class=trade_class,
                fee=fee,
                commission=commission,
                order=None,
                comment=comment,
            )
            trade_class.account_data.positions.append(position)
            trade_class.account_data.history_deals.append(deal)

    return True


# TODO: PYTEST
def __backtest_open_pending_order(
    trade_class: Any,
    symbol: str,
    order_type: ENUM_ORDER_TYPE_PENDING,
    volume: float,
    price: float,
    stop_limit: float = 0,
    stop_price: float = 0,
    profit_price: float = 0,
    expiration: datetime = None,
    comment: str = "",
):
    order_time = datetime.now(timezone.utc)
    current_time_ms = get_timestamp_ms(order_time)

    type_time = (
        ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED
        if expiration
        else ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC
    )

    order = MqlTradeOrder(
        ticket=current_time_ms,
        symbol=symbol,
        type=order_type,
        time_setup=order_time.replace(microsecond=0),
        time_setup_msc=order_time,
        volume_initial=volume,
        volume_current=volume,
        price_stoplimit=stop_limit,
        price_open=price,
        price_current=price,
        tp=profit_price,
        sl=stop_price,
        type_time=type_time,
        time_expiration=expiration,
        state=ENUM_ORDER_STATE.ORDER_STATE_PLACED,
        reason=ENUM_ORDER_REASON.ORDER_REASON_EXPERT,
        magic=trade_class.magic_number,
        type_filling=trade_class.type_filling,
        comment=comment,
    )

    trade_class.account_data.orders.append(order)


# TODO: PYTEST
def __backtest_modify_pending_order(
    trade_class: Any,
    ticket: int,
    price: float,
    stop_price: float = 0,
    profit_price: float = 0,
    expiration: datetime = None,
    comment: str = "",
):
    # Select the order
    order: MqlTradeOrder = get_order(
        list_orders=trade_class.account_data.orders, ticket=ticket
    )

    if expiration:
        type_time = ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED
    else:
        type_time = ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC

    # Change the order attributes
    order.update(
        price_open=price,
        sl=stop_price,
        tp=profit_price,
        comment=comment,
        type_filling=trade_class.type_filling,
        magic=trade_class.magic_number,
        time_expiration=expiration,
        type_time=type_time,
    )


# TODO: PYTEST
def __backtest_modify_position(
    trade_class: Any,
    stop_price: float = None,
    profit_price: float = None,
    position: int = None,
    comment: str = "",
):
    position_not_found_error = CouldNotSelectPosition(
        "[ERROR]: Could not select the position."
    )

    # If position not received, try to get it
    if position is None:
        # If there is only one position opened, get it
        if len(trade_class.account_data.positions) == 1:
            position = trade_class.account_data.positions[0].ticket
        else:
            raise position_not_found_error

    # Get the position from account positions
    position_selected: List[MqlPositionInfo] = [
        mqlposition
        for mqlposition in trade_class.account_data.positions
        if mqlposition.ticket == position
    ]

    # Check if the position exists
    if len(position_selected) != 1:
        raise position_not_found_error

    # Select the position object
    position_selected: MqlSymbolInfo = position_selected[0]

    position_selected.update(
        sl=stop_price,
        tp=profit_price,
        commen=comment,
    )


def __backtest_close_position(
    trade_class: Any,
    position_ticket: int,
    commission: float = 0,
    fee: float = 0,
    comment: str = "",
):
    # Get the position from account positions
    position_selected: List[MqlPositionInfo] = [
        position
        for position in trade_class.account_data.positions
        if position.ticket == position_ticket
    ]

    # Check if the position exists
    if len(position_selected) != 1:
        raise CouldNotSelectPosition("[ERROR]: Could not select the position.")

    # Select the position object
    position_selected: MqlPositionInfo = position_selected[0]

    last_tick = get_last_tick(
        position_selected.symbol,
        trade_class.backtest_env.df.iloc[: trade_class.backtest_env.current_step + 1],
    )

    # Get the oposite direction type and price
    if position_selected.type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY:
        order_type = ENUM_ORDER_TYPE.ORDER_TYPE_SELL
        price = last_tick.bid
    else:
        order_type = ENUM_ORDER_TYPE.ORDER_TYPE_BUY
        price = last_tick.ask

    deal = __backtest_create_a_deal(
        deal_time=last_tick.time,
        position=position_selected,
        symbol=position_selected.symbol,
        order_type=order_type,
        volume=position_selected.volume,
        price=price,
        fee=fee,
        commission=commission,
        order=None,
        comment=comment,
        trade_class=trade_class,
    )

    trade_class.account_data.history_deals.append(deal)

    # Close position
    del trade_class.account_data.positions[
        trade_class.account_data.positions.index(position_selected)
    ]


def decorator_backtest_open_position(func: Callable):
    def check_backtest_account(*args, **kwargs):
        if args[0].account_data.is_backtest_account:
            __backtest_open_position(*args, **kwargs)
            return True
        else:
            return func(*args, **kwargs)

    return check_backtest_account


def decorator_backtest_open_pending_order(func: Callable):
    def check_backtest_account(*args, **kwargs):
        if args[0].account_data.is_backtest_account:
            __backtest_open_pending_order(*args, **kwargs)
            return True
        else:
            return func(*args, **kwargs)

    return check_backtest_account


def decorator_backtest_modify_position(func: Callable):
    def check_backtest_account(*args, **kwargs):
        if args[0].account_data.is_backtest_account:
            __backtest_modify_position(*args, **kwargs)
            return True
        else:
            return func(*args, **kwargs)

    return check_backtest_account


def decorator_backtest_modify_pending_order(func: Callable):
    def check_backtest_account(*args, **kwargs):
        if args[0].account_data.is_backtest_account:
            __backtest_modify_pending_order(*args, **kwargs)
            return True
        else:
            return func(*args, **kwargs)

    return check_backtest_account


def decorator_backtest_close_position(func: Callable):
    def check_backtest_account(*args, **kwargs):
        if args[0].account_data.is_backtest_account:
            __backtest_close_position(*args, **kwargs)
            return True
        else:
            return func(*args, **kwargs)

    return check_backtest_account
