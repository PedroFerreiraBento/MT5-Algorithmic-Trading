from pandas import Series
from typing import Literal
from datetime import datetime
from AlgorithmicTrading.models.metatrader import MqlAccountInfo
import pandas as pd
from AlgorithmicTrading.trade import Trade

# Available moving average types
_MA_TYPE = Literal["SMA", "EMA", "LWMA"]


class Strategy:
    def __init__(
        self,
        account_data: MqlAccountInfo,
    ) -> None:
        self.magic_number = 707070
        self.account_data = account_data

    def run(self, finantial_data: pd.DataFrame):
        backtest_candle = (
            finantial_data.iloc[-1]
            if self.account_data.is_backtest_account
            else None
        )
        trade = Trade(
            account_data=self.account_data,
            magic_number=self.magic_number,
            backtest_last_candle_close=backtest_candle,
        )

    def backtest_run(self, finantial_data: pd.DataFrame):
        pass


class Strategy:
    def __init__(
        self, tp_points: int = 0, sl_points: int = 0, expiration: datetime = None
    ):
        self.tp_points: int = tp_points
        self.sl_points: int = sl_points
        self.expiration: datetime = expiration

    @classmethod
    def backtest_signals(
        cls,
        applied_value: Series,
        fast_period: int = 4,
        slow_period: int = 14,
        ma_type: _MA_TYPE = "EMA",
    ) -> Series:
        signals = (
            applied_value.rolling(slow_period + 1)
            .apply(
                lambda data_range: cls.check_signal(
                    applied_value=data_range,
                    fast_period=fast_period,
                    slow_period=slow_period,
                    ma_type=ma_type,
                )
            )
            .fillna(0)
        )
        signals.name = "MA_Signals"

        return signals

    @classmethod
    def check_signal(
        cls,
        applied_value: Series,
        fast_period: int = 4,
        slow_period: int = 14,
        ma_type: _MA_TYPE = "EMA",
    ) -> int:
        if fast_period >= slow_period:
            raise IndexError(
                f"[ERROR]: The fast period must be higher than the slow period."
            )

        fast_ma = cls.get_ma_value(
            applied_value, period=fast_period, ma_type=ma_type, count=2
        )
        slow_ma = cls.get_ma_value(
            applied_value, period=slow_period, ma_type=ma_type, count=2
        )

        current_fast = fast_ma.iloc[-1]
        current_slow = slow_ma.iloc[-1]
        prev_fast = fast_ma.iloc[-2]
        prev_slow = slow_ma.iloc[-2]

        # Buy signal - Cross above
        if prev_fast < prev_slow and current_fast > current_slow:
            return 1
        # Buy signal - Cross below
        elif prev_fast > prev_slow and current_fast < current_slow:
            return -1

        # Hold signal
        return 0

    @classmethod
    def get_ma_value(
        cls,
        applied_value: Series,
        period: int,
        ma_type: _MA_TYPE = "EMA",
        count: int = 1,
    ) -> Series:
        """Get the moving average(MA) value for a given period

        Args:
            applied_value (Series): Value that the MA will be applied
            period (int): MA period
            ma_type (_MA_TYPE, optional): MA type. Defaults to "EMA".
            count (int, optional): Number of MA values to return. Defaults to 1.

        Raises:
            IndexError: Not enough data was provided
            TypeError: Invalid moving average type

        Returns:
            Series: Moving average value
        """
        # Validate parameters
        if len(applied_value) < period + count - 1:
            raise IndexError(
                f"[ERROR]: Not enough data was provided to find the signals. At least {period + count - 1} rows(period + count - 1) is required."
            )

        required_data = applied_value.iloc[-period - 1 :].copy()

        if ma_type == "SMA":
            ma_data = required_data.rolling(period).mean()
        elif ma_type == "EMA":
            ma_data = required_data.ewm(span=period).mean()
        elif ma_type == "LWMA":
            ma_weights = range(1, period + 1)
            ma_data = required_data.rolling(period).apply(
                lambda row_index: (row_index * ma_weights).sum() / sum(ma_weights),
                raw=True,
            )
        else:
            raise TypeError("[ERROR]: Invalid moving average type selected")

        return ma_data.iloc[-count:]
