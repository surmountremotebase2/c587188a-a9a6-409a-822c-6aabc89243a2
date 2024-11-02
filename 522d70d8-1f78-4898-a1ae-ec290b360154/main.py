from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, MACD, RSI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META"]#, "AMZN", "GOOGL", "NFLX", "TSLA"]
        
    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1hour"
    
    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            ohlcv = data["ohlcv"]
            rsi_value = RSI(ticker, ohlcv, 4)
            macd_data = MACD(ticker, ohlcv, fast=12, slow=26)
            macd_line = macd_data["MACD"]
            signal_line = macd_data["signal"]
            ema9 = EMA(ticker, ohlcv, 9)
            ema21 = EMA(ticker, ohlcv, 21)
            
            # Check for sufficient data
            if not rsi_value or not macd_line or not signal_line or not ema9 or not ema21:
                allocation_dict[ticker] = 0
                continue
            
            current_rsi = rsi_value[-1]
            current_macd_line = macd_line[-1]
            current_signal_line = signal_line[-1]
            current_ema9 = ema9[-1]
            current_ema21 = ema21[-1]
            
            # Logic for entering a buy position
            if (current_macd_line > current_signal_line and
                current_ema9 > current_ema21 and
                current_rsi > 65):
                allocation_dict[ticker] = 1 / len(self.tickers)  # Equally distribute capital
            # Logic for liquidating the position
            elif (current_signal_line > current_macd_line and
                  current_ema9 < current_ema21 and
                  current_rsi < 45):
                allocation_dict[ticker] = 0  # Liquidate position
            else:
                allocation_dict[ticker] = 0  # Default action is to not hold the asset

        return TargetAllocation(allocation_dict)