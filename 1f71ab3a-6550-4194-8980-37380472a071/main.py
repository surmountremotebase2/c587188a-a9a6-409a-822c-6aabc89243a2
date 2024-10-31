from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD"]

    @property
    def assets(self):
        return self.tickers
    
    @property
    def interval(self):
        return "1day"

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            allocation = 0
            
            # Calculate indicators
            ema50 = EMA(ticker, data["ohlcv"], 50)[-1]
            ema200 = EMA(ticker, data["ohlcv"], 200)[-1]
            rsi = RSI(ticker, data["ohlcv"], 14)[-1]
            macd = MACD(ticker, data["ohlcv"], fast=12, slow=26)
            macd_line = macd["MACD"][-1]
            signal_line = macd["signal"][-1]
            
            # Check conditions
            if ema50 > ema200 and 30 < rsi < 70 and macd_line > signal_line:
                allocation = 1 / len(self.tickers)
            
            allocation_dict[ticker] = allocation
        
        return TargetAllocation(allocation_dict)