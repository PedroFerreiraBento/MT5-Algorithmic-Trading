from AlgorithmicTrading.trade.trade import Trade
from AlgorithmicTrading.account import AccountBacktest
from AlgorithmicTrading.models.metatrader import (
    ENUM_ACCOUNT_MARGIN_MODE,
    ENUM_POSITION_TYPE,
)
from AlgorithmicTrading.utils.trades import compute_profit, get_last_tick
from AlgorithmicTrading.ta.support_and_resistance import fit_trendlines_high_low
from AlgorithmicTrading.rates.rates import Rates

import numpy as np
from pandas import DataFrame
from .canva import CandleStickWindow
from gym.spaces import Dict, Discrete, Box


class TradingEnv:
    metadata = {"render_modes": ["human", "ansi"], "render_fps": 4}

    def __init__(
        self,
        df: DataFrame,
        render_mode: str = None,
        symbol: str = "EURUSD",
        render_range: int = 100,
        start_trading_step: int = 100,
        initial_balance: int = 10_000,
        margin_mode: ENUM_ACCOUNT_MARGIN_MODE = ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_NETTING,
        allow_multiple_positions: bool = False,
        stop_out_level: float = 70,
    ) -> None:
        # Validate parameters
        self.validate_parameters(df, render_mode)

        # Environment attributes
        self.observation_space = Dict(
            {
                "trend_slope": Box(low=-np.inf, high=np.inf),
                "price_diff": Box(low=-np.inf, high=np.inf),
                "support_trend_line_slope": Box(low=-np.inf, high=np.inf),
                "resistance_trend_line_slope": Box(low=-np.inf, high=np.inf),
                "volume": Box(low=-np.inf, high=np.inf),
                "currently_holding": Discrete(2),
            }
        )
        self.action_space = Discrete(3)
        self.render_mode = render_mode
        self.support_coefs_c = None
        self.resistance_coefs_c = None
        self.trend_line_interval = 50
        self.trend_line_interval_values = []

        # Trade attribures
        self.df = df
        self.symbol = symbol
        self.symbol_data = Rates.get_symbol_data(symbol)
        self.initial_balance = initial_balance
        self.margin_mode = margin_mode
        self.start_trading_step = start_trading_step
        self.allow_multiple_positions = allow_multiple_positions
        self.stop_out_level = stop_out_level

        # Visualization attributes
        self.render_range = render_range  # render range in visualization
        self.visualization = CandleStickWindow(self)

    def _get_obs(self):
        # Trend slope observation
        trend_slope_interval = 10
        trend_slope = (
            self.df.iloc[self.current_step]["Close"]
            - self.df.iloc[self.current_step - trend_slope_interval]["Open"]
        ) / trend_slope_interval

        # Price difference observation
        price_diff = (
            self.df.iloc[self.current_step]["Close"]
            - self.df.iloc[self.current_step]["Open"]
        )

        # Support and resistance trend lines
        self.trend_line_interval_values = self.df.set_index("Datetime").iloc[
            self.current_step - self.trend_line_interval : self.current_step + 1
        ]
        self.support_coefs_c, self.resist_coefs_c = fit_trendlines_high_low(
            self.trend_line_interval_values["High"],
            self.trend_line_interval_values["Low"],
            self.trend_line_interval_values["Close"],
        )

        return {
            "trend_slope": trend_slope,
            "price_diff": price_diff,
            "support_trend_line_slope": self.support_coefs_c[0],
            "resistance_trend_line_slope": self.resist_coefs_c[0],
            "volume": self.df.iloc[self.current_step]["Volume"],
            "currently_holding": len(self.account.positions),
        }

    def _get_info(self):
        return {}

    def _is_truncated(self):
        return (self.account.equity * 100 / self.initial_balance) < self.stop_out_level

    def reset(self):
        """Reset trading environment"""

        # Reset step back to start
        self.current_step = self.start_trading_step
        self.terminated = False
        self.truncated = False

        # Create a new backtest account
        self.account = AccountBacktest.login(
            balance=self.initial_balance, margin_mode=self.margin_mode
        )

        # Create a new trade object linked with new backtest account
        self.trade = Trade(account_data=self.account, backtest_env=self)

        # Reset net worth
        self.net_worth = np.zeros(len(self.df))

        # Get observation and trade info
        observation = self._get_obs()
        info = self._get_info()

        # Render if its human render mode
        if self.render_mode == "human":
            self.render()

        return observation, info

    def step(
        self,
        action,
        trade_volumes: float = 0.1,
        stop_price: float = 0,
        profit_price: float = 0,
    ):
        if self.terminated or self.truncated:
            raise Exception("[ERROR]: Episode ended!")

        # If there aren't any openned position check if action want to open one
        if (self.allow_multiple_positions) or (not self.account.positions):
            # Open a buy positin
            if action == 1:
                self.trade.buy(
                    symbol=self.symbol,
                    volume=trade_volumes,
                    stop_price=stop_price,
                    profit_price=profit_price,
                )
            # Open a sell positin
            elif action == 2:
                self.trade.sell(
                    symbol=self.symbol,
                    volume=trade_volumes,
                    stop_price=stop_price,
                    profit_price=profit_price,
                )
        # Check if there is a position openned
        elif self.account.positions:
            # If hold close this position
            if action == 0:
                self.trade.close_all_positions()

            # If buy is oposite direction, close and open a new
            elif (
                action == 1
                and self.account.positions[-1].type
                == ENUM_POSITION_TYPE.POSITION_TYPE_SELL
            ):
                self.trade.close_all_positions()
                self.trade.buy(
                    symbol=self.symbol,
                    volume=trade_volumes,
                    stop_price=stop_price,
                    profit_price=profit_price,
                )

            # If sell is oposite direction, close and open a new
            elif (
                action == 2
                and self.account.positions[-1].type
                == ENUM_POSITION_TYPE.POSITION_TYPE_BUY
            ):
                self.trade.close_all_positions()
                self.trade.sell(
                    symbol=self.symbol,
                    volume=trade_volumes,
                    stop_price=stop_price,
                    profit_price=profit_price,
                )

        # Go to the next step
        self.current_step += 1

        # Update position data
        self.__update_positions()

        # Get observation and trade info
        observation = self._get_obs()
        info = self._get_info()
        self.terminated = self.df.iloc[self.current_step].name == self.df.iloc[-1].name
        self.truncated = self._is_truncated()
        reward = self.__compute_reward()

        # Render if its human render mode
        if self.render_mode == "human":
            self.render()

        return observation, reward, self.terminated, self.truncated, info

    def __compute_reward(self) -> float:
        """Compute step reward

        Returns:
            float: Step reward
        """
        # Check if a position was openned
        if not self.account.positions:
            return 0

        reward: float = 0

        # Sum the reward of each openned position
        for position in self.account.positions:
            # Get last tick of current candle and prev candle
            last_tick = get_last_tick(
                self.symbol, self.df.iloc[: self.current_step + 1]
            )
            prev_last_tick = get_last_tick(
                self.symbol, self.df.iloc[: self.current_step]
            )

            # Paid Spread in new positions and not in keeping positions
            if position.type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY:
                price_open = (
                    prev_last_tick.ask
                    if position.price_open == prev_last_tick.ask
                    else prev_last_tick.bid
                )
            else:
                price_open = (
                    prev_last_tick.bid
                    if position.price_open == prev_last_tick.bid
                    else prev_last_tick.ask
                )

            # Compute position profit
            reward += compute_profit(
                account_currency=self.account.currency,
                position_type=position.type,
                price_open=price_open,
                price_close=position.price_current,
                price_volume=position.volume,
                symbol_data=self.symbol_data,
                tick_close=last_tick,
            )

        return reward

    def __update_positions(self) -> None:
        """Update position data"""

        equity = 0
        margin = 0

        # Loop over positions
        for position in self.account.positions:
            position_type = (
                ENUM_POSITION_TYPE.POSITION_TYPE_BUY
                if position.type == ENUM_POSITION_TYPE.POSITION_TYPE_SELL
                else ENUM_POSITION_TYPE.POSITION_TYPE_SELL
            )

            # Get last tick of candle on current step
            last_tick = get_last_tick(
                self.symbol,
                self.trade.backtest_env.df.iloc[
                    : self.trade.backtest_env.current_step + 1
                ],
            )

            # Select price based on position type
            if position_type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY:
                price = last_tick.ask
            else:
                price = last_tick.bid

            # Compute position profit
            profit = compute_profit(
                account_currency=self.account.currency,
                position_type=position.type,
                price_open=position.price_open,
                price_close=price,
                price_volume=position.volume,
                symbol_data=self.symbol_data,
                tick_close=last_tick,
            )

            # Sum positions profit
            equity += profit
            margin += (
                position.price_open
                * self.symbol_data.trade_contract_size
                * position.volume
                / self.account.leverage
            )

            # Update position price and profit
            position.profit = profit
            position.price_current = price

        # Compute equity
        self.account.equity = self.account.balance + equity
        self.account.margin = margin
        self.account.margin_free = self.account.equity - margin
        self.account.margin_level = (
            self.account.equity / self.account.margin if self.account.margin else 1
        ) * 100

    # render environment
    def render(self):
        if self.render_mode == "human":
            # Render the environment to the screen
            self.visualization.show()

        elif self.render == "ansi":
            print(
                f"Step: {self.current_step}, Net Worth: {self.net_worth[self.current_step]}"
            )

    # Close render environment
    def render_close(self):
        self.visualization.close()

    def validate_parameters(self, df: DataFrame, render_mode: str):
        # Validate dataframe
        assert set(
            ["Open", "High", "Low", "Close", "Adj Close", "Volume", "Datetime"]
        ).issubset(df.columns)

        # Validate render mode
        assert render_mode is None or render_mode in self.metadata["render_modes"]

    # Rename df column
    @classmethod
    def set_col_names(
        cls,
        df: DataFrame,
        open_col_name: str = "Open",
        high_col_name: str = "High",
        low_col_name: str = "Low",
        close_col_name: str = "Close",
        adj_close_col_name: str = "Adj Close",
        volume_col_name: str = "Volume",
        datetime_col_name: str = "Datetime",
    ):
        return DataFrame(
            {
                "Open": df[open_col_name],
                "High": df[high_col_name],
                "Low": df[low_col_name],
                "Close": df[close_col_name],
                "Adj Close": df[adj_close_col_name],
                "Volume": df[volume_col_name],
                "Datetime": df[datetime_col_name],
            }
        )
