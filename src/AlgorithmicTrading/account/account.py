import MetaTrader5 as mt5
from AlgorithmicTrading.models.metatrader import MqlAccountInfo
from AlgorithmicTrading.models.metatrader import (
    MqlAccountInfo,
    ENUM_ACCOUNT_TRADE_MODE,
    ENUM_ACCOUNT_STOPOUT_MODE,
    ENUM_ACCOUNT_MARGIN_MODE,
    MqlTradeDeal
)
from AlgorithmicTrading.utils.metatrader import decorator_validate_mt5_connection
import MetaTrader5 as mt5


class AccountLive:
    def __init__(self) -> None:
        self.account_data = None

    @classmethod
    def login(
        cls,
        login: int,
        server: str,
        password: str,
        timeout: int = 60_000,
        portable: bool = False,
        path: str = "",
    ) -> bool:
        """Establish a connection with the MetaTrader 5 terminal.

        Args:
            login (int): Trading account number.
            server (str):  Trade server name.
            password (str): Trading account password.
            timeout (int, optional): Connection timeout in milliseconds. Defaults to 60_000 (1 minute).
            portable (bool, optional):  Flag of the terminal launch in portable mode. Defaults to False.
            path (str, optional):  Path to the metatrader.exe or metatrader64.exe file. Defaults to "".
                Optional unnamed parameter. It is indicated first without a parameter name. If the path is not specified, the module attempts to find the executable file on its own.

        Returns:
            MqlAccountInfo: account data
        """
        # Try to start a connection with the trade server
        if not mt5.initialize(
            path,
            login=login,
            server=server,
            password=password,
            timeout=timeout,
            portable=portable,
        ):
            # Store mess cause shutdown change the last_error() return
            error_message = f"[ERROR]: Login failed, error code = {mt5.last_error()}"

            # Shot down the terminal connection
            mt5.shutdown()

            # Raise a connection error
            raise ConnectionError(error_message)

        print(f"[INFO]: Successfull login to #{login} account")

        # Return a livetrade account object
        return cls.get_data()

    @classmethod
    @decorator_validate_mt5_connection
    def logout(cls) -> None:
        """Shut down connection to the MetaTrader 5 terminal"""
        # Shut down the connection
        mt5.shutdown()

        print("[INFO]: Success logout.")

    @classmethod
    @decorator_validate_mt5_connection
    def get_data(cls) -> MqlAccountInfo:
        """Get updated account data

        Raises:
            ConnectionError: No connection established

        Returns:
            MqlAccountInfo: Updated account data
        """

        return MqlAccountInfo.parse_account(mt5.account_info())


class AccountBacktest:
    @classmethod
    def login(
        cls,
        balance: float = 5_000,
        leverage: int = 100,
        limit_orders: int = 200,
        margin_mode: ENUM_ACCOUNT_MARGIN_MODE = ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING,
    ) -> MqlAccountInfo:
        """Create a backtest account object

        Args:
            balance (float, optional): Account balance. Defaults to 5_000.
            leverage (int, optional): Account leverage. Defaults to 100.
            limit_orders (int, optional): Account limit orders. Defaults to 200.
            margin_mode (ENUM_ACCOUNT_MARGIN_MODE, optional): Account margin mode. Defaults to ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING.

        Returns:
            MqlAccountInfo: Backtest account data
        """

        # Return a backtest account object
        backtest_account = MqlAccountInfo(
            is_backtest_account=True,
            balance=balance,
            leverage=leverage,
            limit_orders=limit_orders,
            margin_mode=margin_mode,
            login=9999999,
            trade_mode=ENUM_ACCOUNT_TRADE_MODE.ACCOUNT_TRADE_MODE_DEMO,
            margin_so_mode=ENUM_ACCOUNT_STOPOUT_MODE.ACCOUNT_STOPOUT_MODE_PERCENT,
            currency_digits=2,
            fifo_close=False,
            credit=0,
            profit=0,
            equity=balance,
            margin=0,
            margin_free=balance,
            margin_level=0,
            margin_so_call=50,
            margin_so_so=30,
            margin_initial=0,
            margin_maintenance=0,
            assets=0,
            liabilities=0,
            commission_blocked=0,
            trade_allowed=True,
            trade_expert=True,
            name="Backtest Name",
            server="Backtest Server",
            currency="USD",
            company="Backtest Company",
        )

        print(f"[INFO]: Successfull backtest account create")

        return backtest_account
