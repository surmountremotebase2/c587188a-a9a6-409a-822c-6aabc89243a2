from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD"]
        # Initial allocation is empty, as we decide allocation based on indicators
        self.allocation = {ticker: 0 for ticker in self.tickers}
        self.budget = 1000  # Preset investment budget ($)
        
    @property
    def assets(self):
        return self.tickers
    
    @property
    def interval(self):
        return "1hour"
    
    def run(self, data):
        for ticker in self.tickers:
            try:
                ema9 = EMA(ticker, data, length=9)
                ema21 = EMA(ticker, data, length=21)
                rsi = RSI(ticker, data, length=4)
                macd = MACD(ticker, data, fast=12, slow=26, signal=9)
                
                if ema9[-1] > ema21[-1] and rsi[-1] > 65 and macd["MACD"][-1] > macd["signal"][-1]:
                    # Allocate fraction based on the number of tickers for simplicity, could be optimized
                    self.allocation[ticker] = self.budget / len(self.tickers)
                elif ema9[-1] < ema21[-1] and rsi[-1] < 45 and macd["MACD"][-1] < macd["signal"][-1]:
                    self.allocation[ticker] = 0  # Liquidate the position
                else:
                    # Existing allocation preserved if conditions for change are not met
                    continue
            except IndexError:
                # In case the EMA, RSI, or MACD lists are empty (e.g., not enough data points)
                log(f"Not enough data for {ticker}, skipping allocation.")
                self.allocation[ticker] = 0
        
        # Convert dollar allocation to percentage for TargetAllocation compatibility
        allocation_percentage = {ticker: val / self.budget for ticker, val in self.allocation.items()}
        
        return TargetAllocation(allocation_percentage)