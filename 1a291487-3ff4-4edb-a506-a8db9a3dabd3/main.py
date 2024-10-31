from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD"]
        # Allocate $1000 among the assets equally. This is a simplification; in real scenarios, 
        # the allocation should be dynamic based on portfolio optimization or other criteria.
        self.initial_allocation = 1000 / len(self.tickers)

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        allocation = {}
        
        for ticker in self.tickers:
            ema9 = EMA(ticker, data, 9)
            ema21 = EMA(ticker, data, 21)
            rsi = RSI(ticker, data, 4)
            macd = MACD(ticker, data, fast=12, slow=26)
            
            if not ema9 or not ema21 or not rsi or not macd["MACD"] or not macd["signal"]:
                log(f"Insufficient data for {ticker}")
                allocation[ticker] = 0  # Insufficient data to make a decision
                continue
            
            # Check if EMA9 > EMA21, RSI(4) > 65, and MACD line > signal line
            if ema9[-1] > ema21[-1] and rsi[-1] > 65 and macd["MACD"][-1] > macd["signal"][-1]:
                allocation[ticker] = self.initial_allocation  # Buy or keep the position
            # Liquidate the position when EMA9 < EMA21 and RSI(4) < 45 and MACD line < signal line
            elif ema9[-1] < ema21[-1] and rsi[-1] < 45 and macd["MACD"][-1] < macd["signal"][-1]:
                allocation[ticker] = 0  # Sell or do not enter a position
            else:
                # For simplicity, we're not changing the allocation for this condition
                # However, in practice, you might want to hold, adjust the allocation, or set other conditions
                allocation[ticker] = 0
        
        # Normalize the allocation to ensure the sum is within [0, 1] range
        total_allocation = sum(allocation.values())
        if total_allocation > 0:
            normalized_allocation = {ticker: alloc/total_allocation for ticker, alloc in allocation.items()}
        else:
            normalized_allocation = allocation  # In case no investment is advised, pass the original allocation
            
        return TargetAllocation(normalized_allocation)