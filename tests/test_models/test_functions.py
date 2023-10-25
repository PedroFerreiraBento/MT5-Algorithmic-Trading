from AlgorithmicTrading.models.metatrader import validate_prices, ENUM_ORDER_TYPE
import pytest


class TestFunctions:
    """Assert MT5 models functions"""

    def test_validate_prices(self):
        # Validate stop loss ----------------------------------------------------------------------
        with pytest.raises(ValueError) as excinfo:
            validate_prices(price=1, sl=1.1, order_type=ENUM_ORDER_TYPE.ORDER_TYPE_BUY)

        assert str(excinfo.value) == "Invalid stop loss"

        with pytest.raises(ValueError) as excinfo:
            validate_prices(price=1, sl=0.9, order_type=ENUM_ORDER_TYPE.ORDER_TYPE_SELL)

        assert str(excinfo.value) == "Invalid stop loss"
        
        # Validate Take Profit --------------------------------------------------------------------
        with pytest.raises(ValueError) as excinfo:
            validate_prices(price=1, tp=0.9, order_type=ENUM_ORDER_TYPE.ORDER_TYPE_BUY)

        assert str(excinfo.value) == "Invalid take profit"

        with pytest.raises(ValueError) as excinfo:
            validate_prices(price=1, tp=1.1, order_type=ENUM_ORDER_TYPE.ORDER_TYPE_SELL)

        assert str(excinfo.value) == "Invalid take profit"

        # Validate stop limit ---------------------------------------------------------------------
        with pytest.raises(ValueError) as excinfo:
            validate_prices(
                price=1, stoplimit=1.1, order_type=ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP_LIMIT
            )

        assert str(excinfo.value) == "Invalid stop limit"

        with pytest.raises(ValueError) as excinfo:
            validate_prices(
                price=1, stoplimit=0.9, order_type=ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP_LIMIT
            )

        assert str(excinfo.value) == "Invalid stop limit"
