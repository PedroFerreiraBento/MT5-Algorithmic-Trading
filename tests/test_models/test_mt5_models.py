import MetaTrader5 as mt5
from AlgorithmicTrading.models.metatrader import (
    ENUM_TRADE_REQUEST_ACTIONS,
    ENUM_ORDER_TYPE,
    MqlSymbolInfo,
    MqlTradeRequest,
)
from AlgorithmicTrading.utils.exceptions import NotExpectedParseType
import pytest
from datetime import datetime, timezone


class TestMqlSymbolInfo:
    """Assert MT5 models"""

    test_symbol = mt5.SymbolInfo(
        [
            False,
            0,
            True,
            True,
            0,
            0,
            0,
            0,
            0,
            0,
            1697575601,
            3,
            8,
            True,
            10,
            0,
            4,
            0,
            0,
            0,
            0,
            1,
            1,
            3,
            False,
            7,
            1,
            127,
            0,
            0,
            0,
            149.817,
            149.824,
            148.959,
            149.825,
            149.83,
            148.967,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.001,
            0.6674453529117305,
            0.6674453529117305,
            0.6674809934787107,
            0.001,
            100000.0,
            0.0,
            0.0,
            0.0,
            0.01,
            500.0,
            0.01,
            0.0,
            -0.1,
            -0.6,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            149.516,
            149.53,
            0.0,
            0.0,
            0.0,
            0.0,
            100000.0,
            0.1919,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            "",
            "",
            "USD",
            "JPY",
            "USD",
            "",
            "US Dollar vs Yen",
            "",
            "",
            "",
            "USDJPY",
            "https://www.mql5.com/en/quotes/currencies/usdjpy",
            "Forex\\USDJPY",
        ]
    )

    def test_parse(self):
        dict_symbol = {
            "time": self.test_symbol.time,
            "spread": self.test_symbol.spread,
            "digits": self.test_symbol.digits,
            "ask": self.test_symbol.ask,
            "bid": self.test_symbol.bid,
            "volume_min": self.test_symbol.volume_min,
            "volume_max": self.test_symbol.volume_max,
            "volume_step": self.test_symbol.volume_step,
            "trade_tick_size": self.test_symbol.trade_tick_size,
            "trade_contract_size": self.test_symbol.trade_contract_size,
            "trade_tick_value_profit": self.test_symbol.trade_tick_value_profit,
            "trade_tick_value_loss": self.test_symbol.trade_tick_value_loss,
            "currency_base": self.test_symbol.currency_base,
            "currency_profit": self.test_symbol.currency_profit,
            "description": self.test_symbol.description,
            "name": self.test_symbol.name,
        }

        # Assert parse object
        assert MqlSymbolInfo(**dict_symbol) == MqlSymbolInfo.parse_symbol(
            self.test_symbol
        )

        # Assert parse type
        with pytest.raises(NotExpectedParseType) as excinfo:
            MqlSymbolInfo.parse_symbol(None)

        assert isinstance(excinfo.value, NotExpectedParseType)

        # Assert validate datetime
        assert MqlSymbolInfo.parse_symbol(self.test_symbol).time == datetime(
            2023, 10, 17, 17, 46, 41, tzinfo=timezone.utc
        )
