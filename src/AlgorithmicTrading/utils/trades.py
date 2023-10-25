from AlgorithmicTrading.models.metatrader import (
    ENUM_POSITION_TYPE,
    MqlTick,
    MqlSymbolInfo,
    MqlTradeOrder,
)
from AlgorithmicTrading.rates import Rates
from AlgorithmicTrading.utils.exceptions import PairNotAvailable
import datetime
import pandas as pd
from typing import List
from collections import Counter


def find_pair(currency_1: str, currency_2: str) -> str:
    pairs = [
        name
        for name in Rates.get_symbols_names()
        if currency_1 in name and currency_2 in name
    ]

    # No pairs available
    if not pairs:
        raise PairNotAvailable(
            f"[ERROR]: Could not find a pair with currencies: {currency_1} and {currency_2}"
        )

    # More then one pair found - Atypical
    if len(pairs) > 1:
        pairs = [pair for pair in pairs if str.endswith(currency_2)]

    return pairs[0]


def convert_cross_currency_value(
    value: float,
    value_currency: str,
    target_currency: str,
    date_from: datetime,
    position_type: ENUM_POSITION_TYPE,
):
    # Direct currency convertion
    if target_currency == "USD" or value_currency == "USD":
        convert_pair = find_pair(currency_1=value_currency, currency_2=target_currency)

        convert_tick: MqlTick = Rates.get_specific_tick(
            symbol=convert_pair, date_from=date_from
        )

        if convert_pair.endswith(target_currency):
            value_target = value * (
                convert_tick.ask
                if position_type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY
                else convert_tick.bid
            )
        else:
            value_target = value / (
                convert_tick.ask
                if position_type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY
                else convert_tick.bid
            )

    # Cross conversion
    else:
        # Base convert to USD
        convert_base_pair = find_pair(currency_1=value_currency, currency_2="USD")
        convert_tick_base: MqlTick = Rates.get_specific_tick(
            symbol=convert_base_pair, date_from=date_from
        )

        if convert_base_pair.endswith("USD"):
            value_base = value * (
                convert_tick_base.ask
                if position_type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY
                else convert_tick_base.bid
            )
        else:
            value_base = value / (
                convert_tick_base.ask
                if position_type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY
                else convert_tick_base.bid
            )

        # USD convert to target
        convert_target_pair = find_pair(currency_1="USD", currency_2=target_currency)

        convert_tick_target: MqlTick = Rates.get_specific_tick(
            symbol=convert_target_pair, date_from=date_from
        )

        if convert_target_pair.endswith(target_currency):
            value_target = value_base * (
                convert_tick_target.ask
                if position_type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY
                else convert_tick_target.bid
            )
        else:
            value_target = value_base / (
                convert_tick_target.ask
                if position_type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY
                else convert_tick_target.bid
            )

    return value_target


def compute_profit(
    price_open: float,
    price_close: float,
    price_volume: float,
    tick_close: MqlTick,
    symbol_data: MqlSymbolInfo,
    position_type: ENUM_POSITION_TYPE,
    account_currency: str,
) -> float:
    """Compute position profit

    Args:
        price_open (float): Position price open
        price_close (float): Position price close
        price_volume (float): Position volume
        tick_close (MqlTick): Tick with close value
        symbol_data (MqlSymbolInfo): Information about Symbol traded
        position_type (ENUM_POSITION_TYPE): Position type
        account_currency (str): Trade account currency base

    Returns:
        float: Profit
    """

    # OBS: This value is in target currency. Ex: USDJPY, will be in JPY currency
    tick_value = (
        symbol_data.trade_contract_size * price_volume * symbol_data.trade_tick_size
    )

    # Get how many ticks the position worth
    ticks_count = (price_close - price_open) / symbol_data.trade_tick_size

    # Reverse it if it's buying a SELL position
    if position_type != ENUM_POSITION_TYPE.POSITION_TYPE_BUY:
        ticks_count *= -1

    # If account currency is the base of pair, convert the target value to base value
    if symbol_data.currency_base == account_currency:
        tick_value /= (
            tick_close.ask if ENUM_POSITION_TYPE.POSITION_TYPE_BUY else tick_close.bid
        )

    # Cross currency
    elif not symbol_data.currency_profit == account_currency:
        tick_value = convert_cross_currency_value(
            value=tick_value,
            value_currency=symbol_data.currency_profit,
            target_currency=account_currency,
            date_from=tick_close["Datetime"],
        )

    # It is rounded because the computer operation can turn a 2.0 into 2.0000000006348273
    profit = round(ticks_count * tick_value, 5)

    return profit


def get_last_tick(symbol: str, financial_data: pd.DataFrame) -> MqlTick:
    """Get last tick of the last DataFrame candle

    Args:
        symbol (str): Symbol pair
        financial_data (pd.DataFrame): Dataframe

    Returns:
        MqlTick: Last candle tick
    """

    # Get the two last candles
    time_candle_last1 = financial_data["Datetime"].iloc[-1]
    time_candle_last2 = financial_data["Datetime"].iloc[-2]
    time_candle_last3 = financial_data["Datetime"].iloc[-3]
    time_candle_last4 = financial_data["Datetime"].iloc[-4]

    # Compute time difference
    timediff1 = time_candle_last1 - time_candle_last2
    timediff2 = time_candle_last2 - time_candle_last3
    timediff3 = time_candle_last3 - time_candle_last4

    timediff = Counter([timediff1, timediff2, timediff3]).most_common(1)[0][0]

    # Get a 5 minutes tick interval
    interval = datetime.timedelta(minutes=5)

    # Get last tick date
    date_to = time_candle_last1 + timediff
    date_from = time_candle_last1
    # date_from = date_to - interval

    # Get last tick
    last_tick = Rates.get_ticks_range(symbol, date_from, date_to)[-1]

    return last_tick


def get_order(list_orders: List[MqlTradeOrder], ticket: int) -> MqlTradeOrder:
    # Find the order
    order: List[MqlTradeOrder] = [
        order for order in list_orders if order.ticket == ticket
    ]
    if not order:
        raise ValueError(f"[ERROR]: Order with ticket #{ticket} not found")

    return order[0]
