import pandas as pd
from typing import List

from AlgorithmicTrading.models.metatrader import MqlAccountInfo
from AlgorithmicTrading.strategies.base import BaseStrategy

from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from ta.volume import AccDistIndexIndicator, OnBalanceVolumeIndicator


class Strategy(BaseStrategy):
    def __init__(self, account_data: MqlAccountInfo, symbols: List[str]) -> None:
        # Set a constant strategy magic number
        super.__init__(
            magic_number=707070,
            account_data=account_data,
            symbols=symbols,
        )

    @classmethod
    def features_engineering(cls, finantial_data: pd.DataFrame) -> pd.DataFrame:
        # Features - Price based
        finantial_data = finantial_data[["open", "high", "low", "close", "tick_volume"]]

        # Features - Returns
        finantial_data["Target - returns"] = (
            finantial_data.close - finantial_data.open
        ).shift(-1)

        # Features - Short-term moving averages
        finantial_data["Feature - 5 SMA"] = finantial_data.close.ewm(span=5).mean()
        finantial_data["Feature - 10 SMA"] = finantial_data.close.ewm(span=10).mean()
        finantial_data["Feature - 20 SMA"] = finantial_data.close.ewm(span=20).mean()

        # Features - Medium-term moving averages
        finantial_data["Feature - 30 SMA"] = finantial_data.close.ewm(span=30).mean()
        finantial_data["Feature - 50 SMA"] = finantial_data.close.ewm(span=50).mean()
        finantial_data["Feature - 100 SMA"] = finantial_data.close.ewm(span=100).mean()

        # Features - Long-term moving averages
        finantial_data["Feature - 200 SMA"] = finantial_data.close.ewm(span=200).mean()
        finantial_data["Feature - 250 SMA"] = finantial_data.close.ewm(span=250).mean()

        # Features - RSI
        indicator_rsi_14 = RSIIndicator(close=finantial_data.close, window=14)
        indicator_rsi_21 = RSIIndicator(close=finantial_data.close, window=21)

        finantial_data["Feature - 14 RSI"] = indicator_rsi_14.rsi()
        finantial_data["Feature - 21 RSI"] = indicator_rsi_21.rsi()
        finantial_data["Feature - 14 RSI SMA"] = (
            finantial_data["Feature - 14 RSI"].ewm(span=14).mean()
        )
        finantial_data["Feature - 21 RSI SMA"] = (
            finantial_data["Feature - 21 RSI"].ewm(span=14).mean()
        )

        # Features - MACD
        indicator_macd = MACD(
            close=finantial_data.close,
            window_slow=26,
            window_fast=12,
            window_sign=9,
        )

        finantial_data["Feature - MACD Line"] = indicator_macd.macd()
        finantial_data["Feature - MACD Signal Line"] = indicator_macd.macd_signal()
        finantial_data["Feature - MACD Diff"] = indicator_macd.macd_diff()

        # Features - Bollinger bands
        indicator_bollinger_bands = BollingerBands(
            close=finantial_data.close,
            window=20,
            window_dev=2,
        )

        finantial_data[
            "Feature - Bollinger Bands High Band"
        ] = indicator_bollinger_bands.bollinger_hband()
        finantial_data[
            "Feature - Bollinger Bands Mid Band"
        ] = indicator_bollinger_bands.bollinger_mavg()
        finantial_data[
            "Feature - Bollinger Bands Low Band"
        ] = indicator_bollinger_bands.bollinger_lband()
        finantial_data[
            "Feature - Bollinger Bands P Band"
        ] = indicator_bollinger_bands.bollinger_pband()
        finantial_data[
            "Feature - Bollinger Bands W Band"
        ] = indicator_bollinger_bands.bollinger_wband()

        # Features - Accumulation/Distribution Index
        indicator_acc_dist = AccDistIndexIndicator(
            high=finantial_data.high,
            low=finantial_data.low,
            close=finantial_data.close,
            volume=finantial_data.tick_volume,
        )

        finantial_data["Feature - Acc/Dist Index"] = indicator_acc_dist.acc_dist_index()

        return finantial_data

    def run(self, finantial_data: pd.DataFrame):
        # Initialize the strategy
        finantial_data, trade = self.initialize_run(finantial_data=finantial_data)

        # Get features
        finantial_data = self.features_engineering(finantial_data)
