from AlgorithmicTrading.models.metatrader import (
    ENUM_POSITION_TYPE,
    ENUM_ORDER_TYPE,
    MqlTick,
    MqlSymbolInfo,
)
from AlgorithmicTrading.rates import Rates
from AlgorithmicTrading.utils.exceptions import PairNotAvailable
import datetime
import pandas as pd


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
    value: float, value_currency: str, target_currency: str, date_from: datetime
):
    # Direct conversion
    if target_currency == "USD" or value_currency == "USD":
        convert_pair = find_pair(currency_1=value_currency, currency_2=target_currency)

        convert_tick: MqlTick = Rates.get_specific_tick(
            symbol=convert_pair, date_from=date_from
        )

        if convert_pair.endswith(target_currency):
            value_target = value * (
                convert_tick.ask if value >= 0 else convert_tick.bid
            )
        else:
            value_target = value / (
                convert_tick.ask if value >= 0 else convert_tick.bid
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
                convert_tick_base.ask if value >= 0 else convert_tick_base.bid
            )
        else:
            value_base = value / (
                convert_tick_base.ask if value >= 0 else convert_tick_base.bid
            )

        # USD convert to target
        convert_target_pair = find_pair(currency_1="USD", currency_2=target_currency)

        convert_tick_target: MqlTick = Rates.get_specific_tick(
            symbol=convert_target_pair, date_from=date_from
        )

        if convert_target_pair.endswith(target_currency):
            value_target = value_base * (
                convert_tick_target.ask if value_base >= 0 else convert_tick_target.bid
            )
        else:
            value_target = value_base / (
                convert_tick_target.ask if value_base >= 0 else convert_tick_target.bid
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
    # This values is in base currency
    tick_value = (
        symbol_data.trade_contract_size * price_volume * symbol_data.trade_tick_size
    )

    # Compute profit count ticks change
    ticks_count = (price_close - price_open) / symbol_data.trade_tick_size

    # Reverse it if it is a sell position
    if position_type == ENUM_POSITION_TYPE.POSITION_TYPE_SELL:
        ticks_count *= -1

    # Base currency
    if symbol_data.currency_base == account_currency:
        tick_value /= tick_close.ask if ticks_count >= 0 else tick_close.bid
    # Cross currency
    elif not symbol_data.currency_profit == account_currency:
        tick_value = convert_cross_currency_value(
            value=tick_value,
            value_currency=symbol_data.currency_profit,
            target_currency=account_currency,
            date_from=tick_close.time,
        )

    # It is rounded because the computer operation can turn a 2.0 into 2.0000000006348273
    profit = round(ticks_count * tick_value, 5)

    return profit


def get_last_tick(symbol: str, financial_data: pd.DataFrame) -> MqlTick:
    time_last_candle_1 = financial_data.time.iloc[-1]
    time_last_candle_2 = financial_data.time.iloc[-2]

    timediff = time_last_candle_1 - time_last_candle_2

    date_from = time_last_candle_1
    date_to = time_last_candle_1 + timediff

    last_tick = Rates.get_ticks_range(symbol, date_from, date_to)

    return last_tick[-1]

def validate_prices(
    price: float,
    sl: float,
    tp: float,
    stoplimit: float, 
    order_type: ENUM_ORDER_TYPE,
) -> None:

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

    # Check the Stop Limit position
    if stoplimit and (
        # Buy stop limit
        (order_type == buy_stop_limit and stoplimit >= price)
        # Sell stop limit
        or (order_type == sell_stop_limit and stoplimit <= price)
    ):
        raise ValueError("Invalid stop limit")

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