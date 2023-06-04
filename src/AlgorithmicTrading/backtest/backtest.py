import pandas as pd
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
from AlgorithmicTrading.utils.trades import compute_profit, get_last_tick
from typing import Any


def __get_deal_type(
    order_type: ENUM_ORDER_TYPE,
) -> ENUM_DEAL_TYPE:
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
    create_position: bool = True,
):
    # Modify/Close position
    if not create_position:
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
    account_currency: str,
) -> float:
    symbol_data: MqlSymbolInfo = Rates.get_symbol_data(symbol)

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
    order_type: ENUM_ORDER_TYPE,
    volume: float,
    price: float,
    position: MqlPositionInfo,
    trade_class: Any,
    fee: float = 0,
    commission: float = 0,
    order: int = None,
    comment: str = "",
    create_position: bool = True,
) -> MqlTradeDeal:
    # Generate a deal ticket
    deal_time = datetime.now(timezone.utc)
    random_ticket = get_timestamp_ms(deal_time)

    # Get order ID
    order_id = (
        order if order is not None else get_timestamp_ms(datetime.now(timezone.utc))
    )

    # Get deal type
    deal_type = __get_deal_type(order_type=order_type)

    # Get entry or out
    entry = __get_entry(
        order_type=order_type,
        volume=volume,
        position=position,
        create_position=create_position,
    )

    # Get deal profit
    if not create_position and entry != ENUM_DEAL_ENTRY.DEAL_ENTRY_IN:
        last_tick = get_last_tick(symbol, trade_class.backtest_financial_data)

        close_volume = (
            volume if entry != ENUM_DEAL_ENTRY.DEAL_ENTRY_INOUT else position.volume
        )

        profit = __backtest_get_profit(
            symbol=symbol,
            account_currency=trade_class.account_data.currency,
            position_type=position.type,
            price_open=position.price_open,
            price_close=position.price_current,
            price_volume=close_volume,
            last_tick=last_tick,
        )
    else:
        profit = 0

    deal = MqlTradeDeal(
        ticket=random_ticket,
        order=order_id,
        time=deal_time.replace(microsecond=0),
        time_msc=deal_time,
        type=deal_type,
        entry=entry,
        magic=trade_class.magic_number,
        position_id=position.ticket,
        reason=ENUM_DEAL_REASON.DEAL_REASON_EXPERT,
        volume=volume,
        price=price,
        commission=commission,
        swap=0,
        profit=profit,
        fee=fee,
        symbol=symbol,
        comment=comment,
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
    position_time = datetime.now(timezone.utc)
    current_time_ms = get_timestamp_ms(position_time)

    last_candle = trade_class.backtest_financial_data.iloc[-1]

    price = last_candle.close

    symbol_data = Rates.get_symbol_data(symbol)

    if order_type == ENUM_ORDER_TYPE_MARKET.ORDER_TYPE_BUY:
        tick_size = symbol_data.trade_tick_size
        price += last_candle.spread * tick_size

    position_type = ENUM_POSITION_TYPE(order_type)

    position = MqlPositionInfo(
        ticket=current_time_ms,
        time=position_time,
        time_msc=position_time,
        time_update=position_time.replace(microsecond=0),
        time_update_msc=position_time,
        type=position_type,
        magic=trade_class.magic_number,
        identifier=current_time_ms,
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
            symbol=symbol,
            order_type=order_type,
            volume=volume,
            price=position.price_current,
            trade_class=trade_class,
            fee=fee,
            commission=commission,
            order=None,
            comment="",
            create_position=True,
        )
        trade_class.account_data.positions.append(position)
        trade_class.account_data.history_deals.append(deal)
    # Netting account
    else:
        # Check if there is a position already opened
        if trade_class.account_data.positions:
            opened_position = trade_class.account_data.positions[0]

            position.ticket = opened_position.ticket
            position.time = opened_position.time
            position.time_msc = opened_position.time_msc
            position.identifier = opened_position.identifier
            position.volume = opened_position.volume
            position.type = opened_position.type
            position.price_open = opened_position.price_open

            # Check if there is a position on the other direction
            if opened_position.type != position_type:
                # Equal volumes
                if opened_position.volume == volume:
                    deal = __backtest_create_a_deal(
                        position=position,
                        symbol=symbol,
                        order_type=order_type,
                        volume=volume,
                        price=position.price_current,
                        trade_class=trade_class,
                        fee=fee,
                        commission=commission,
                        order=None,
                        comment="",
                        create_position=False,
                    )

                    trade_class.account_data.history_deals.append(deal)

                    # Close position
                    del trade_class.account_data.positions[0]

                # Higher volume - Keep direction
                elif opened_position.volume > volume:
                    deal = __backtest_create_a_deal(
                        position=position,
                        symbol=symbol,
                        order_type=order_type,
                        volume=volume,
                        price=position.price_current,
                        trade_class=trade_class,
                        fee=fee,
                        commission=commission,
                        order=None,
                        comment="",
                        create_position=False,
                    )

                    position.volume = round(position.volume - volume, 2)

                    trade_class.account_data.positions[0] = position
                    trade_class.account_data.history_deals.append(deal)

                # Lower volume - Revert
                elif opened_position.volume < volume:
                    # Change the identifier
                    position.identifier = current_time_ms

                    # Close the opened direction position
                    deal_close = __backtest_create_a_deal(
                        position=position,
                        symbol=symbol,
                        order_type=order_type,
                        volume=volume,
                        price=position.price_current,
                        trade_class=trade_class,
                        fee=fee,
                        commission=commission,
                        order=None,
                        comment="",
                        create_position=False,
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

                    # Open a new direction deal
                    deal_open = __backtest_create_a_deal(
                        position=position,
                        symbol=symbol,
                        order_type=order_type,
                        volume=position.volume,
                        price=position.price_current,
                        trade_class=trade_class,
                        fee=fee,
                        commission=commission,
                        order=None,
                        comment="",
                        create_position=True,
                    )

                    trade_class.account_data.positions[0] = position
                    trade_class.account_data.history_deals.append(deal_close)
                    trade_class.account_data.history_deals.append(deal_open)

            # Check if there is a position on the same direction
            elif opened_position.type == position_type:
                deal = __backtest_create_a_deal(
                    position=position,
                    symbol=symbol,
                    order_type=order_type,
                    volume=volume,
                    price=position.price_current,
                    trade_class=trade_class,
                    fee=fee,
                    commission=commission,
                    order=None,
                    comment="",
                    create_position=False,
                )

                # Compute a new volume and price
                total_volume = round(position.volume + volume, 2)
                mean_price = (
                    (opened_position.price_open * opened_position.volume)
                    + (position.price_open * volume)
                ) / total_volume
                position.volume = total_volume
                position.price_open = mean_price

                # Replace position
                trade_class.account_data.positions[0] = position

                trade_class.account_data.history_deals.append(deal)

        # No positions opened
        else:
            deal = __backtest_create_a_deal(
                position=position,
                symbol=symbol,
                order_type=order_type,
                volume=volume,
                price=position.price_current,
                trade_class=trade_class,
                fee=fee,
                commission=commission,
                order=None,
                comment="",
                create_position=True,
            )
            trade_class.account_data.positions.append(position)
            trade_class.account_data.history_deals.append(deal)

    return True


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


def decorator_backtest_open_position(func: Callable):
    def check_backtest_account(*args, **kwargs):
        if args[0].account_data.is_backtest_account:
            return __backtest_open_position(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    return check_backtest_account


def decorator_backtest_open_pending_order(func: Callable):
    def check_backtest_account(*args, **kwargs):
        if args[0].account_data.is_backtest_account:
            return __backtest_open_pending_order(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    return check_backtest_account
