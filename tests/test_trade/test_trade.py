from AlgorithmicTrading.trade.trade import Trade
from AlgorithmicTrading.models.metatrader import ENUM_ACCOUNT_MARGIN_MODE, ENUM_DEAL_TYPE, ENUM_DEAL_ENTRY, ENUM_POSITION_TYPE
from AlgorithmicTrading.backtest.environment.environment import TradingEnv
from AlgorithmicTrading.account.account import AccountBacktest, AccountLive
from AlgorithmicTrading.config.config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
from AlgorithmicTrading.rates.rates import Rates
from AlgorithmicTrading.models.metatrader import ENUM_TIMEFRAME
from datetime import datetime, timezone

class TestTrade:
    # Start a mt5 connection
    account = AccountLive.login(login=MT5_LOGIN, server=MT5_SERVER, password=MT5_PASSWORD)
    
    # Set a fixed rates interval
    test_rates = TradingEnv.set_col_names(
            Rates.get_candles_range(
                "EURUSD", 
                date_from=datetime(2022, 1, 1, tzinfo=timezone.utc), 
                date_to=datetime(2022, 1, 7, tzinfo=timezone.utc), 
                timeframe=ENUM_TIMEFRAME.TIMEFRAME_M15
            ).reset_index(), 
            adj_close_col_name="close",
            close_col_name="close",
            datetime_col_name="time",
            high_col_name="high",
            low_col_name="low",
            open_col_name="open",
            volume_col_name="tick_volume",
        )
    
    def test_netting_sell_positions(self):
        # Test netting positions
        env = TradingEnv(df=self.test_rates, allow_multiple_positions=True, initial_balance=100_000, margin_mode=ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_NETTING)
        env.reset()
        
        # Execute a sell order
        env.step(2, trade_volumes=0.1)
        
        # Assert sell position
        assert env.account.positions[-1].price_open == 1.12973
        assert env.account.positions[-1].price_current == 1.13002
        assert env.account.positions[-1].profit == -2.9
        assert env.account.positions[-1].volume == 0.1
        
        # Assert deal info
        assert env.account.history_deals[-1].type == ENUM_DEAL_TYPE.DEAL_TYPE_SELL
        assert env.account.history_deals[-1].entry == ENUM_DEAL_ENTRY.DEAL_ENTRY_IN
        assert env.account.history_deals[-1].volume == 0.1
        assert env.account.history_deals[-1].price == 1.12973
        assert env.account.history_deals[-1].profit == 0
        
        # Re-Execute a sell order
        env.step(2, trade_volumes=0.1)
        
        assert env.account.positions[-1].price_open == 1.129805
        assert env.account.positions[-1].price_current == 1.12998
        assert env.account.positions[-1].profit == -3.5
        assert env.account.positions[-1].volume == 0.2
        
    def test_netting_buy_positions(self):
        # Test netting positions
        env = TradingEnv(df=self.test_rates, allow_multiple_positions=True, initial_balance=100_000, margin_mode=ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_NETTING)
        env.reset()
        
        # Execute a buy order
        env.step(1, trade_volumes=0.1)
        
        # Assert buy position
        assert env.account.positions[-1].price_open == 1.12986
        assert env.account.positions[-1].price_current == 1.12988
        assert env.account.positions[-1].profit == 0.2
        assert env.account.positions[-1].volume == 0.1
        
        # Assert deal info
        assert env.account.history_deals[-1].type == ENUM_DEAL_TYPE.DEAL_TYPE_BUY
        assert env.account.history_deals[-1].entry == ENUM_DEAL_ENTRY.DEAL_ENTRY_IN
        assert env.account.history_deals[-1].volume == 0.1
        assert env.account.history_deals[-1].price == 1.12986
        assert env.account.history_deals[-1].profit == 0
                
        # Re-Execute a buy order
        env.step(1, trade_volumes=0.1)
        
        assert env.account.positions[-1].price_open == 1.12994
        assert env.account.positions[-1].price_current == 1.12985
        assert env.account.positions[-1].profit == -1.8
        assert env.account.positions[-1].volume == 0.2
        
    def test_netting_revert_buy_positions(self):
        # Test netting positions
        env = TradingEnv(df=self.test_rates, allow_multiple_positions=True, initial_balance=100_000, margin_mode=ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_NETTING)
        env.reset()
        
        # Execute a buy order
        env.step(1, trade_volumes=0.1)
                
        # Execute a sell order
        env.step(2, trade_volumes=0.2)
        
        # Assert deal info
        assert env.account.history_deals[-1].type == ENUM_DEAL_TYPE.DEAL_TYPE_SELL
        assert env.account.history_deals[-1].entry == ENUM_DEAL_ENTRY.DEAL_ENTRY_INOUT
        assert env.account.history_deals[-1].volume == 0.2
        assert env.account.history_deals[-1].price == 1.12988
        assert env.account.history_deals[-1].profit == 0.2
        
        # Assert reverted position info
        assert env.account.positions[-1].price_open == 1.12988
        assert env.account.positions[-1].price_current == 1.12998
        assert env.account.positions[-1].profit == -1.0
        assert env.account.positions[-1].volume == 0.1
        assert env.account.positions[-1].type == ENUM_POSITION_TYPE.POSITION_TYPE_SELL
        
    def test_netting_revert_sell_positions(self):
        # Test netting positions
        env = TradingEnv(df=self.test_rates, allow_multiple_positions=True, initial_balance=100_000, margin_mode=ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_NETTING)
        env.reset()
        
        # Execute a buy order
        env.step(2, trade_volumes=0.1)
                
        # Execute a sell order
        env.step(1, trade_volumes=0.2)
        
        # Assert deal info
        assert env.account.history_deals[-1].type == ENUM_DEAL_TYPE.DEAL_TYPE_BUY
        assert env.account.history_deals[-1].entry == ENUM_DEAL_ENTRY.DEAL_ENTRY_INOUT
        assert env.account.history_deals[-1].volume == 0.2
        assert env.account.history_deals[-1].price == 1.13002
        assert env.account.history_deals[-1].profit == -2.9
        
        # Assert reverted position info
        assert env.account.positions[-1].price_open == 1.13002
        assert env.account.positions[-1].price_current == 1.12985
        assert env.account.positions[-1].profit == -1.7
        assert env.account.positions[-1].volume == 0.1
        assert env.account.positions[-1].type == ENUM_POSITION_TYPE.POSITION_TYPE_BUY
        
    def test_close_position(self):
        # Test netting positions
        env = TradingEnv(df=self.test_rates, allow_multiple_positions=True, initial_balance=100_000, margin_mode=ENUM_ACCOUNT_MARGIN_MODE.ACCOUNT_MARGIN_MODE_RETAIL_NETTING)
        env.reset()
        
        # Execute a buy order
        env.step(1, trade_volumes=0.1)
        
        # Close positions
        env.trade.close_all_positions()
        
        # Assert closed positions
        assert not len(env.account.positions)
        
        # Assert deal info
        assert env.account.history_deals[-1].type == ENUM_DEAL_TYPE.DEAL_TYPE_SELL
        assert env.account.history_deals[-1].entry == ENUM_DEAL_ENTRY.DEAL_ENTRY_OUT
        assert env.account.history_deals[-1].volume == 0.1
        assert env.account.history_deals[-1].price == 1.12988
        assert env.account.history_deals[-1].profit == 0.2
