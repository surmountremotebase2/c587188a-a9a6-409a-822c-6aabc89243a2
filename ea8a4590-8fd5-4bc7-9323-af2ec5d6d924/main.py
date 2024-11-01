from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        
    @property
    def interval(self):
        # Assuming daily prices provide sufficient resolution for this strategy
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            # Calculate EMA9 and EMA21
            ema9 = EMA(ticker, data, 9)
            ema21 = EMA(ticker, data, 21)
            
            # Ensure we have sufficient data to make a comparison
            if ema9 is not None and ema21 is not None and len(ema9) > 0 and len(ema21) > 0:
                # Compare the last available EMA values
                if ema9[-1] > ema21[-1]:
                    # EMA9 > EMA21, fully invest (1)
                    allocation_dict[ticker] = 1
                elif ema9[-1] < ema21[-1]:
                    # EMA9 < EMA21, liquidate (0)
                    allocation_dict[ticker] = 0
                else:
                    # If EMAs are equal, or for any reason not able to decide, hold current position
                    # Not trading signals to hold, assuming it to remain as it is
                    log(f"No clear EMA crossover signal for {ticker}")
            else:
                # If data is not available to compute EMAs, avoid trading
                log(f"Insufficient EMA data available for {ticker}, no action taken.")
                allocation_dict[ticker] = 0  # Or consider handling this case differently as needed

        return TargetAllocation(allocation_dict)