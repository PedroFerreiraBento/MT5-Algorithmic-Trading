import MetaTrader5 as mt5
import pandas as pd
from AlgorithmicTrading.models.metatrader import ENUM_TIMEFRAME
from AlgorithmicTrading.utils.metatrader import (
    decorator_validate_mt5_connection,
    validate_mt5_int_size,
)
from datetime import datetime
import numpy as np
from AlgorithmicTrading.models.metatrader import MqlSymbolInfo


class Rates:
    # Get data ------------------------------------------------------------------------
    @classmethod
    @decorator_validate_mt5_connection
    def get_symbols_names(cls) -> list:
        """Get symbols names

        Returns:
            list: symbols names
        """

        return [symbol.name for symbol in mt5.symbols_get()]

    @classmethod
    @decorator_validate_mt5_connection
    def get_symbol_data(cls, symbol: str) -> MqlSymbolInfo:
        """Get symbol

        Args:
            symbol (str): Symbol

        Returns:
            MqlSymbolInfo: symbols data
        """

        cls.validate_symbol(symbol=symbol)

        return mt5.symbols_get(symbol)

    # Get candles
    @classmethod
    @decorator_validate_mt5_connection
    def get_last_n_candles(
        cls,
        symbol: str,
        timeframe: ENUM_TIMEFRAME = ENUM_TIMEFRAME.TIMEFRAME_M5,
        n_candles: int = 10_000,
    ) -> pd.DataFrame:
        """Get last 'n' candles

        Args:
            symbol (str): Requested symbol
            timeframe (ENUM_TIMEFRAME, optional): Requested timeframe. Defaults to ENUM_TIMEFRAME.TIMEFRAME_M5.
            n_candles (int, optional): Requested number of candles. Defaults to 10_000.

        Returns:
            pd.DataFrame: Requested OHLC data
        """

        # Validate parameters
        cls.validate_symbol(symbol)
        validate_mt5_int_size(n_candles)
        cls.validate_count_candles(n_candles)

        # Request OHLC data
        requested_data = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_candles)

        # Validate request result
        cls.validate_request_result(requested_data)

        # Convert to DataFrame
        ohlc_data = pd.DataFrame(requested_data)

        # Convert timestamp to datetime
        ohlc_data["time"] = pd.to_datetime(ohlc_data.time, unit="s", utc=True)

        return ohlc_data

    @classmethod
    @decorator_validate_mt5_connection
    def get_candles_before(
        cls,
        symbol: str,
        timeframe: ENUM_TIMEFRAME = ENUM_TIMEFRAME.TIMEFRAME_M5,
        date_to: datetime = datetime.now(),
        n_candles: int = 10_000,
    ) -> pd.DataFrame:
        """Get candles from a specified datetime

        Args:
            symbol (str): Requested symbol
            timeframe (ENUM_TIMEFRAME, optional): Requested timeframe. Defaults to ENUM_TIMEFRAME.TIMEFRAME_M5.
            date_to (datetime, optional): To date. Defaults to datetime.now().
            n_candles (int, optional): Requested number of candles. Defaults to 10_000.

        Returns:
            pd.DataFrame: Requested OHLC data
        """
        # Validate parameters
        cls.validate_symbol(symbol)
        validate_mt5_int_size(n_candles)
        cls.validate_count_candles(n_candles)
        cls.validate_date(date_to)

        # Request OHLC data
        requested_data = mt5.copy_rates_from(symbol, timeframe, date_to, n_candles)

        # Validate request result
        cls.validate_request_result(requested_data)

        # Convert to DataFrame
        ohlc_data = pd.DataFrame(requested_data)

        # Convert timestamp to datetime
        ohlc_data["time"] = pd.to_datetime(ohlc_data.time, unit="s", utc=True)

        return ohlc_data

    @classmethod
    @decorator_validate_mt5_connection
    def get_candles_range(
        cls,
        symbol: str,
        date_from: datetime,
        date_to: datetime = datetime.now(),
        timeframe: ENUM_TIMEFRAME = ENUM_TIMEFRAME.TIMEFRAME_M5,
    ) -> pd.DataFrame:
        """Get candles from a specified datetime

        Args:
            symbol (str): Requested symbol
            date_from (datetime, optional): From date.
            date_to (datetime, optional): To date. Defaults to datetime.now().
            timeframe (ENUM_TIMEFRAME, optional): Requested timeframe. Defaults to ENUM_TIMEFRAME.TIMEFRAME_M5.

        Returns:
            pd.DataFrame: Requested OHLC data
        """

        # Validate parameters
        cls.validate_symbol(symbol)
        cls.validate_date(date_from)
        cls.validate_date(date_to)
        cls.validate_date_range(date_from, date_to)

        # Request OHLC data
        requested_data = mt5.copy_rates_range(symbol, timeframe, date_from, date_to)

        # Validate request result
        cls.validate_request_result(requested_data)

        # Convert to DataFrame
        ohlc_data = pd.DataFrame(requested_data)

        # Convert timestamp to datetime
        ohlc_data["time"] = pd.to_datetime(ohlc_data.time, unit="s", utc=True)

        return ohlc_data

    # Get ticks
    @classmethod
    @decorator_validate_mt5_connection
    def get_last_n_ticks(
        cls,
        symbol: str,
        n_ticks: int = 50,
    ) -> pd.DataFrame:
        """Get candles from a specified datetime

        Args:
            symbol (str): Requested symbol
            n_ticks (int, optional): Requested number of ticks. Defaults to 50.

        Returns:
            pd.DataFrame: Requested ticks
        """

        # Validate parameters
        cls.validate_symbol(symbol)
        validate_mt5_int_size(n_ticks)

        # Request OHLC data
        requested_data = mt5.copy_ticks_from(
            symbol, datetime.now(), n_ticks, mt5.COPY_TICKS_ALL
        )

        # Validate request result
        cls.validate_request_result(requested_data)

        # Convert to DataFrame
        ticks_data = pd.DataFrame(requested_data)

        # Convert timestamp to datetime
        ticks_data["time"] = pd.to_datetime(ticks_data.time, unit="s", utc=True)
        ticks_data["time_msc"] = pd.to_datetime(
            ticks_data.time_msc, unit="ms", utc=True
        )

        return ticks_data

    # Validation ----------------------------------------------------------------------
    @classmethod
    def validate_count_candles(cls, n_candles: int) -> None:
        """Validate max bars

        Validate if requested candles is higher tha max bars

        Args:
            n_candles (int): Requested candles count

        Raises:
            ValueError: The number of candles cannot be higher than terminal chart max bars
        """
        # Check max bars
        max_bars = mt5.terminal_info().maxbars
        if n_candles >= max_bars:
            raise ValueError(
                f"[ERROR]: The number of candles cannot be higher than terminal chart max bars({max_bars})"
            )

    @classmethod
    def validate_symbol(cls, symbol: str) -> None:
        """Validate requested symbol

        Args:
            symbol (str): Requested symbol

        Raises:
            ValueError: The selected symbol is not in the symbols list
        """

        # Check valid symbol
        if symbol not in cls.get_symbols_names():
            raise ValueError("[ERROR]: The selected symbol is not in the symbols list")

    @classmethod
    def validate_request_result(cls, request_result: np.ndarray) -> None:
        """Validate request result

        Args:
            request_result (np.ndarray): request result

        Raises:
            TypeError: Request Error
            ValueError: No data returned
        """
        # Check request success
        if request_result is None:
            raise TypeError("[ERROR]: Request error, please check the request format")

        # Check empty request data
        if not len(request_result):
            raise ValueError("[ERROR]: No data returned")

    @classmethod
    def validate_date(cls, date: datetime) -> None:
        """Validate date

        Args:
            date (datetime): Date to validate

        Raises:
            ValueError: Request datetime can not be higher than the current datetime
        """

        if date > datetime.now():
            raise ValueError(
                "[ERROR]: Request datetime can not be higher than the current datetime"
            )

    @classmethod
    def validate_date_range(cls, date_from: datetime, date_to: datetime):
        """Validate date range

        Args:
            date_from (datetime): From date
            date_to (datetime): To date

        Raises:
            ValueError: Invalid date range
        """
        if date_from >= date_to:
            raise ValueError("[ERROR]: Invalid date range")
