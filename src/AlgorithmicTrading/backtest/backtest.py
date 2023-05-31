import pandas as pd
from AlgorithmicTrading.models.metatrader import (
    MqlPositionInfo,
    MqlAccountInfo,
    MqlTradeDeal,
    ENUM_POSITION_REASON,
    ENUM_ORDER_TYPE_MARKET,
    ENUM_POSITION_TYPE,
    ENUM_ACCOUNT_MARGIN_MODE,
    ENUM_DEAL_TYPE,
    ENUM_ORDER_TYPE,
    ENUM_DEAL_ENTRY,
    ENUM_DEAL_REASON,
)
from AlgorithmicTrading.utils.dates import get_timestamp_ms
from typing import Callable
import AlgorithmicTrading.trade.trade as trade
from datetime import datetime


class Backtest:
    def __init__(
        self, account_data: MqlAccountInfo, backtest_last_candle: pd.DataFrame
    ) -> None:
        self.account_data = account_data
        self.backtest_last_candle = backtest_last_candle
        self.candle_time = self.backtest_last_candle.time.to_pydatetime()
        self.current_time_ms = get_timestamp_ms(self.candle_time)

    def open_position(
        self,
        symbol: str,
        order_type: ENUM_ORDER_TYPE_MARKET,
        volume: float,
        stop_price: float = 0,
        profit_price: float = 0,
        comment: str = "",
    ):
        position = MqlPositionInfo(
            ticket=self.current_time_ms,
            time=self.candle_time,
            time_msc=self.candle_time,
            time_update=self.candle_time,
            time_update_msc=self.candle_time,
            type=ENUM_POSITION_TYPE(order_type),
            magic=self.magic_number,
            identifier=self.current_time_ms,
            reason=ENUM_POSITION_REASON.POSITION_REASON_EXPERT,
            volume=volume,
            price_open=self.backtest_last_candle.close,
            sl=stop_price,
            tp=profit_price,
            price_current=self.backtest_last_candle.close,
            swap=0,
            profit=0,
            symbol=symbol,
            comment=comment,
            external_id=None,
        )

        if (
            self.account_data
            == ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING
        ):
            self.account_data.positions.append(position)
        else:
            # Check if there is a position on the other direction
            if (
                self.account_data.positions
                and self.account_data.positions[0].type != order_type
            ):
                # Equal volumes
                if self.account_data.positions[0].volume == volume:
                    del self.account_data.positions[0]

                # Higher volume
                if self.account_data.positions[0].volume > volume:
                    pass
            else:
                self.account_data.positions.append(position)


def __get_deal_type(
    order_type: ENUM_ORDER_TYPE,
):
    if order_type in (ENUM_ORDER_TYPE.ORDER_TYPE_BUY):
        return ENUM_DEAL_TYPE.DEAL_TYPE_BUY

    if order_type in (ENUM_ORDER_TYPE.ORDER_TYPE_SELL):
        return ENUM_DEAL_TYPE.DEAL_TYPE_SELL

    raise TypeError("[ERROR]: Invalid order type")


def __get_entry(
    volume: float,
    order_type: ENUM_ORDER_TYPE,
    position: MqlPositionInfo = None,
):
    if position is not None:
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

        else:
            return ENUM_DEAL_ENTRY.DEAL_ENTRY_IN

    else:
        return ENUM_DEAL_ENTRY.DEAL_ENTRY_IN


def __get_entry(
    price_open: float,
    price_close: float,
    price_volume: float,
):
    pass


def __backtest_create_a_deal(
    symbol: str,
    order_type: ENUM_ORDER_TYPE,
    volume: float,
    price: float,
    time: datetime,
    time_ms: int,
    fee: float = 0,
    commission: float = 0,
    order: int = None,
    magic: int = None,
    comment: str = None,
    position: MqlPositionInfo = None,
):
    # Generate a deal ticket
    random_ticket = get_timestamp_ms(datetime.utcnow())

    # Get deal type
    deal_type = __get_deal_type(order_type=order_type)

    # Get position ID
    position_id = position.ticket if position is not None else random_ticket

    # Get order ID
    order_id = order if order is not None else random_ticket

    # Get entry or out
    entry = __get_entry(order_type=order_type, volume=volume, position=position)

    deal = MqlTradeDeal(
        ticket=random_ticket,
        order=order_id,
        time=time,
        time_msc=time_ms,
        type=deal_type,
        entry=entry,
        magic=magic,
        position_id=position_id,
        reason=ENUM_DEAL_REASON.DEAL_REASON_EXPERT,
        volume=volume,
        price=price,
        commission=commission,
        swap=0,
        profit=0,
        fee=fee,
        symbol=symbol,
        comment=comment,
        external_id=None,
    )

    return deal


def decorator_backtest_open_position(func: Callable):
    def backtest_open_position(
        trade_class: trade.Trade,
        symbol: str,
        order_type: ENUM_ORDER_TYPE_MARKET,
        volume: float,
        stop_price: float = 0,
        profit_price: float = 0,
        comment: str = "",
    ):
        candle_time = trade_class.backtest_last_candle.time.to_pydatetime()
        current_time_ms = get_timestamp_ms(candle_time)

        position = MqlPositionInfo(
            ticket=current_time_ms,
            time=candle_time,
            time_msc=candle_time,
            time_update=candle_time,
            time_update_msc=candle_time,
            type=ENUM_POSITION_TYPE(order_type),
            magic=trade_class.magic_number,
            identifier=current_time_ms,
            reason=ENUM_POSITION_REASON.POSITION_REASON_EXPERT,
            volume=volume,
            price_open=trade_class.backtest_last_candle.close,
            sl=stop_price,
            tp=profit_price,
            price_current=trade_class.backtest_last_candle.close,
            swap=0,
            profit=0,
            symbol=symbol,
            comment=comment,
            external_id=None,
        )

        if (
            trade_class.account_data
            == ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING
        ):
            trade_class.account_data.positions.append(position)
        else:
            # Check if there is a position on the other direction
            if (
                trade_class.account_data.positions
                and trade_class.account_data.positions[0].type != order_type
            ):
                # Equal volumes
                if trade_class.account_data.positions[0].volume == volume:
                    deal = MqlTradeDeal(
                        ticket=int,
                        order=int,
                        time=candle_time,
                        time_msc=current_time_ms,
                        type=ENUM_DEAL_TYPE,
                        entry=ENUM_DEAL_ENTRY,
                        magic=int,
                        position_id=int,
                        reason=ENUM_DEAL_REASON,
                        volume=float,
                        price=float,
                        commission=float,
                        swap=float,
                        profit=float,
                        fee=float,
                        symbol=str,
                        comment=str,
                        external_id=str,
                    )

                    trade_class.account_data.history_deals.append(deal)
                    del trade_class.account_data.positions[0]

                # Higher volume
                if trade_class.account_data.positions[0].volume > volume:
                    pass
            else:
                trade_class.account_data.positions.append(position)

    def check_backtest_account(*args, **kwargs):
        if args[0].account_data.is_backtest_account:
            return backtest_open_position(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    return check_backtest_account
