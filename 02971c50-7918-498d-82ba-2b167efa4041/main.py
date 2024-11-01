from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        # No need to add specific data sources like OHLCV as Surmount handles it based on assets & interval
    
    @property
    def interval(self):
        # The frequency for the EMA calculation, daily is chosen here
        return "1day"
    
    @property
    def assets(self):
        # Specifies the stocks of interest for the strategy
        return self.tickers
    
    def run(self, data):
        allocation = {}
        for ticker in self.tickers:
            # Calculate both EMAs for each ticker
            ema9 = EMA(ticker, data["ohlcv"], length=9)
            ema21 = EMA(ticker, data["ohlcv"], length=21)
            
            # Ensure we have enough data points for both EMAs to make a decision
            if ema9 is not None and ema21 is not None and len(ema9) > 0 and len(ema21) > 0:
                # If EMA9 is above EMA21, full allocation (1) else no allocation (0)
                allocation[ticker] = 1.0 if ema9[-1] > ema21[-1] else 0.0
            else:
                # Default to no allocation if there's insufficient data
                allocation[ticker] = 0.0
                
        return TargetAllocation(allocation)