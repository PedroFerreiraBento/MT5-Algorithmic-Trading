from AlgorithmicTrading.models.metatrader import (
    ENUM_TRADE_REQUEST_ACTIONS,
    ENUM_POSITION_TYPE,
    ENUM_POSITION_REASON,
    ENUM_DEAL_TYPE,
    ENUM_DEAL_ENTRY,
    ENUM_DEAL_REASON,
    ENUM_ORDER_REASON,
    ENUM_ORDER_TYPE,
    ENUM_ORDER_TYPE_MARKET,
    ENUM_ORDER_TYPE_PENDING,
    ENUM_ORDER_TYPE_FILLING,
    ENUM_ORDER_TYPE_TIME,
    ENUM_ORDER_STATE,
    ENUM_TRADE_RETCODE,
    ENUM_TIMEFRAME,
    ENUM_CHECK_CODE,
    ENUM_ACCOUNT_TRADE_MODE,
    ENUM_ACCOUNT_MARGIN_MODE,
    ENUM_ACCOUNT_STOPOUT_MODE,
)


class TestEnumValues:
    """Assert MT5 enum values to check if some value changed or is not available anymore"""

    def test_enum_trade_request_actions(self):
        assert ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_DEAL == 1
        assert ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_PENDING == 5
        assert ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_SLTP == 6
        assert ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_MODIFY == 7
        assert ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_REMOVE == 8
        assert ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_CLOSE_BY == 10

    def test_enum_position_type(self):
        assert ENUM_POSITION_TYPE.POSITION_TYPE_BUY == 0
        assert ENUM_POSITION_TYPE.POSITION_TYPE_SELL == 1

    def test_enum_position_reason(self):
        assert ENUM_POSITION_REASON.POSITION_REASON_CLIENT == 0
        assert ENUM_POSITION_REASON.POSITION_REASON_MOBILE == 1
        assert ENUM_POSITION_REASON.POSITION_REASON_WEB == 2
        assert ENUM_POSITION_REASON.POSITION_REASON_EXPERT == 3

    def test_enum_deal_type(self):
        assert ENUM_DEAL_TYPE.DEAL_TYPE_BUY == 0
        assert ENUM_DEAL_TYPE.DEAL_TYPE_SELL == 1
        assert ENUM_DEAL_TYPE.DEAL_TYPE_BALANCE == 2
        assert ENUM_DEAL_TYPE.DEAL_TYPE_CREDIT == 3
        assert ENUM_DEAL_TYPE.DEAL_TYPE_CHARGE == 4
        assert ENUM_DEAL_TYPE.DEAL_TYPE_CORRECTION == 5
        assert ENUM_DEAL_TYPE.DEAL_TYPE_BONUS == 6
        assert ENUM_DEAL_TYPE.DEAL_TYPE_COMMISSION == 7
        assert ENUM_DEAL_TYPE.DEAL_TYPE_COMMISSION_DAILY == 8
        assert ENUM_DEAL_TYPE.DEAL_TYPE_COMMISSION_MONTHLY == 9
        assert ENUM_DEAL_TYPE.DEAL_TYPE_COMMISSION_AGENT_DAILY == 10
        assert ENUM_DEAL_TYPE.DEAL_TYPE_COMMISSION_AGENT_MONTHLY == 11
        assert ENUM_DEAL_TYPE.DEAL_TYPE_INTEREST == 12
        assert ENUM_DEAL_TYPE.DEAL_TYPE_BUY_CANCELED == 13
        assert ENUM_DEAL_TYPE.DEAL_TYPE_SELL_CANCELED == 14
        assert ENUM_DEAL_TYPE.DEAL_DIVIDEND == 15
        assert ENUM_DEAL_TYPE.DEAL_DIVIDEND_FRANKED == 16
        assert ENUM_DEAL_TYPE.DEAL_TAX == 17

    def test_enum_deal_entry(self):
        assert ENUM_DEAL_ENTRY.DEAL_ENTRY_IN == 0
        assert ENUM_DEAL_ENTRY.DEAL_ENTRY_OUT == 1
        assert ENUM_DEAL_ENTRY.DEAL_ENTRY_INOUT == 2
        assert ENUM_DEAL_ENTRY.DEAL_ENTRY_OUT_BY == 3

    def test_enum_deal_reason(self):
        assert ENUM_DEAL_REASON.DEAL_REASON_CLIENT == 0
        assert ENUM_DEAL_REASON.DEAL_REASON_MOBILE == 1
        assert ENUM_DEAL_REASON.DEAL_REASON_WEB == 2
        assert ENUM_DEAL_REASON.DEAL_REASON_EXPERT == 3
        assert ENUM_DEAL_REASON.DEAL_REASON_SL == 4
        assert ENUM_DEAL_REASON.DEAL_REASON_TP == 5
        assert ENUM_DEAL_REASON.DEAL_REASON_SO == 6
        assert ENUM_DEAL_REASON.DEAL_REASON_ROLLOVER == 7
        assert ENUM_DEAL_REASON.DEAL_REASON_VMARGIN == 8
        assert ENUM_DEAL_REASON.DEAL_REASON_SPLIT == 9

    def test_enum_order_reason(self):
        assert ENUM_ORDER_REASON.ORDER_REASON_CLIENT == 0
        assert ENUM_ORDER_REASON.ORDER_REASON_MOBILE == 1
        assert ENUM_ORDER_REASON.ORDER_REASON_WEB == 2
        assert ENUM_ORDER_REASON.ORDER_REASON_EXPERT == 3
        assert ENUM_ORDER_REASON.ORDER_REASON_SL == 4
        assert ENUM_ORDER_REASON.ORDER_REASON_TP == 5
        assert ENUM_ORDER_REASON.ORDER_REASON_SO == 6

    def test_enum_order_type(self):
        assert ENUM_ORDER_TYPE.ORDER_TYPE_BUY == 0
        assert ENUM_ORDER_TYPE.ORDER_TYPE_SELL == 1
        assert ENUM_ORDER_TYPE.ORDER_TYPE_BUY_LIMIT == 2
        assert ENUM_ORDER_TYPE.ORDER_TYPE_SELL_LIMIT == 3
        assert ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP == 4
        assert ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP == 5
        assert ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP_LIMIT == 6
        assert ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP_LIMIT == 7
        assert ENUM_ORDER_TYPE.ORDER_TYPE_CLOSE_BY == 8

        assert (
            ENUM_ORDER_TYPE.get_order_name(ENUM_ORDER_TYPE.ORDER_TYPE_BUY.name) == "BUY"
        )

    def test_enum_order_type_market(self):
        assert ENUM_ORDER_TYPE_MARKET.ORDER_TYPE_BUY == ENUM_ORDER_TYPE.ORDER_TYPE_BUY
        assert ENUM_ORDER_TYPE_MARKET.ORDER_TYPE_SELL == ENUM_ORDER_TYPE.ORDER_TYPE_SELL

    def test_enum_order_type_pending(self):
        assert (
            ENUM_ORDER_TYPE_PENDING.ORDER_TYPE_BUY_LIMIT
            == ENUM_ORDER_TYPE.ORDER_TYPE_BUY_LIMIT
        )
        assert (
            ENUM_ORDER_TYPE_PENDING.ORDER_TYPE_BUY_STOP
            == ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP
        )
        assert (
            ENUM_ORDER_TYPE_PENDING.ORDER_TYPE_BUY_STOP_LIMIT
            == ENUM_ORDER_TYPE.ORDER_TYPE_BUY_STOP_LIMIT
        )
        assert (
            ENUM_ORDER_TYPE_PENDING.ORDER_TYPE_SELL_LIMIT
            == ENUM_ORDER_TYPE.ORDER_TYPE_SELL_LIMIT
        )
        assert (
            ENUM_ORDER_TYPE_PENDING.ORDER_TYPE_SELL_STOP
            == ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP
        )
        assert (
            ENUM_ORDER_TYPE_PENDING.ORDER_TYPE_SELL_STOP_LIMIT
            == ENUM_ORDER_TYPE.ORDER_TYPE_SELL_STOP_LIMIT
        )

    def test_enum_order_type_filling(self):
        assert ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_FOK == 0
        assert ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_IOC == 1
        assert ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_RETURN == 2
        assert ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_BOC == 3

    def test_enum_order_type_time(self):
        assert ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC == 0
        assert ENUM_ORDER_TYPE_TIME.ORDER_TIME_DAY == 1
        assert ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED == 2
        assert ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED_DAY == 3

    def test_enum_order_state(self):
        assert ENUM_ORDER_STATE.ORDER_STATE_STARTED == 0
        assert ENUM_ORDER_STATE.ORDER_STATE_PLACED == 1
        assert ENUM_ORDER_STATE.ORDER_STATE_CANCELED == 2
        assert ENUM_ORDER_STATE.ORDER_STATE_PARTIAL == 3
        assert ENUM_ORDER_STATE.ORDER_STATE_FILLED == 4
        assert ENUM_ORDER_STATE.ORDER_STATE_REJECTED == 5
        assert ENUM_ORDER_STATE.ORDER_STATE_EXPIRED == 6
        assert ENUM_ORDER_STATE.ORDER_STATE_REQUEST_ADD == 7
        assert ENUM_ORDER_STATE.ORDER_STATE_REQUEST_MODIFY == 8
        assert ENUM_ORDER_STATE.ORDER_STATE_REQUEST_CANCEL == 9

    def test_enum_trade_return_code(self):
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_REQUOTE == 10004
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_REJECT == 10006
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_CANCEL == 10007
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_PLACED == 10008
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_DONE == 10009
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_DONE_PARTIAL == 10010
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_ERROR == 10011
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_TIMEOUT == 10012
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_INVALID == 10013
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_INVALID_VOLUME == 10014
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_INVALID_PRICE == 10015
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_INVALID_STOPS == 10016
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_TRADE_DISABLED == 10017
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_MARKET_CLOSED == 10018
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_NO_MONEY == 10019
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_PRICE_CHANGED == 10020
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_PRICE_OFF == 10021
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_INVALID_EXPIRATION == 10022
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_ORDER_CHANGED == 10023
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_TOO_MANY_REQUESTS == 10024
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_NO_CHANGES == 10025
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_SERVER_DISABLES_AT == 10026
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_CLIENT_DISABLES_AT == 10027
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_LOCKED == 10028
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_FROZEN == 10029
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_INVALID_FILL == 10030
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_CONNECTION == 10031
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_ONLY_REAL == 10032
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_LIMIT_ORDERS == 10033
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_LIMIT_VOLUME == 10034
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_INVALID_ORDER == 10035
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_POSITION_CLOSED == 10036
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_INVALID_CLOSE_VOLUME == 10038
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_CLOSE_ORDER_EXIST == 10039
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_LIMIT_POSITIONS == 10040
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_REJECT_CANCEL == 10041
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_LONG_ONLY == 10042
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_SHORT_ONLY == 10043
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_CLOSE_ONLY == 10044
        assert ENUM_TRADE_RETCODE.TRADE_RETCODE_FIFO_CLOSE == 10045

    def test_enum_timeframe(self):
        assert ENUM_TIMEFRAME.TIMEFRAME_M1 == 1
        assert ENUM_TIMEFRAME.TIMEFRAME_M2 == 2
        assert ENUM_TIMEFRAME.TIMEFRAME_M3 == 3
        assert ENUM_TIMEFRAME.TIMEFRAME_M4 == 4
        assert ENUM_TIMEFRAME.TIMEFRAME_M5 == 5
        assert ENUM_TIMEFRAME.TIMEFRAME_M6 == 6
        assert ENUM_TIMEFRAME.TIMEFRAME_M10 == 10
        assert ENUM_TIMEFRAME.TIMEFRAME_M15 == 15
        assert ENUM_TIMEFRAME.TIMEFRAME_M20 == 20
        assert ENUM_TIMEFRAME.TIMEFRAME_M30 == 30
        assert ENUM_TIMEFRAME.TIMEFRAME_H1 == 16385
        assert ENUM_TIMEFRAME.TIMEFRAME_H2 == 16386
        assert ENUM_TIMEFRAME.TIMEFRAME_H3 == 16387
        assert ENUM_TIMEFRAME.TIMEFRAME_H4 == 16388
        assert ENUM_TIMEFRAME.TIMEFRAME_H6 == 16390
        assert ENUM_TIMEFRAME.TIMEFRAME_H8 == 16392
        assert ENUM_TIMEFRAME.TIMEFRAME_H12 == 16396
        assert ENUM_TIMEFRAME.TIMEFRAME_D1 == 16408
        assert ENUM_TIMEFRAME.TIMEFRAME_MN1 == 49153

    def test_enum_check_code(self):
        assert ENUM_CHECK_CODE.CHECK_RETCODE_OK == 1
        assert ENUM_CHECK_CODE.CHECK_RETCODE_ERROR == 2
        assert ENUM_CHECK_CODE.CHECK_RETCODE_RETRY == 3

    def test_enum_account_trade_mode(self):
        assert ENUM_ACCOUNT_TRADE_MODE.ACCOUNT_TRADE_MODE_DEMO == 0
        assert ENUM_ACCOUNT_TRADE_MODE.ACCOUNT_TRADE_MODE_CONTEST == 1
        assert ENUM_ACCOUNT_TRADE_MODE.ACCOUNT_TRADE_MODE_REAL == 2

    def test_enum_account_margin_mode(self):
        assert ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_NETTING == 0
        assert ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_EXCHANGE == 1
        assert ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING == 2

    def test_enum_account_stopout_mode(self):
        assert ENUM_ACCOUNT_STOPOUT_MODE.ACCOUNT_STOPOUT_MODE_PERCENT == 0
        assert ENUM_ACCOUNT_STOPOUT_MODE.ACCOUNT_STOPOUT_MODE_MONEY == 1
