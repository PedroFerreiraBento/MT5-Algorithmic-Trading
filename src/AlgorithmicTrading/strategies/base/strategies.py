import pandas as pd
from typing import List
from datetime import datetime

from AlgorithmicTrading.models.metatrader import MqlAccountInfo
from AlgorithmicTrading.trade import Trade
from AlgorithmicTrading.rates import Rates


class BaseStrategy:
    def __init__(
        self, account_data: MqlAccountInfo, magic_number: int, symbols: List[str]
    ) -> None:
        self.magic_number = magic_number
        self.account_data = account_data
        self.symbols = symbols

    def initialize_run(self, symbol: str, date_from: datetime, date_to: datetime) -> tuple:
        finantial_data = Rates.get_candles_range(
            symbol=symbol,
            date_from=date_from,
            date_to=date_to,
        )

        # Create a trade class
        trade = Trade(
            account_data=self.account_data,
            magic_number=self.magic_number,
            backtest_financial_data=finantial_data,
        )

        # Return the copy and the trade class
        return finantial_data, trade

    def backtest_run(self, finantial_data: pd.DataFrame) -> None:
        def execute_backtest(row):
            # Find the row index
            row_index_loc = finantial_data.index.get_loc(row.name)

            # Slice the data
            sliced_data = finantial_data.iloc[: row_index_loc + 1]

            # Run strategy
            self.run(finantial_data=sliced_data)

        # Run the strategy for each candle
        finantial_data.apply(lambda row: execute_backtest(row), axis=1)
