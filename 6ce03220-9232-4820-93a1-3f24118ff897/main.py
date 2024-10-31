from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the asset(s) you want to trade
        self.tickers = ["AAPL"]  # For example, trading Apple stock

    @property
    def interval(self):
        # Define the interval for data points. E.g., using "1day" for daily trading signals
        return "1day"

    @property
    def assets(self):
        # Return the list of tickers this strategy operates on
        return self.tickers

    def run(self, data):
        # Initialize allocation as empty to hold the target allocations
        allocation_dict = {}
        for ticker in self.tickers:
            try:
                # Calculate EMA9 and EMA21 for the ticker
                ema9 = EMA(ticker, data["ohlcv"], 9)
                ema21 = EMA(ticker, data["ohlcv"], 21)

                # Check if enough data points are available
                if len(ema9) > 0 and len(ema21) > 0:
                    # Buy signal: When EMA9 is greater than EMA21
                    if ema9[-1] > ema21[-1]:
                        allocation_dict[ticker] = 1.0  # Invest 100% of the allocation into the ticker
                    # Sell signal: When EMA21 is greater than EMA9
                    elif ema21[-1] > ema9[-1]:
                        allocation_dict[ticker] = 0  # Allocate 0% indicating selling off the position
                    else:
                        # If no clear signal is present, no allocation is changed
                        allocation_dict[ticker] = 0
                else:
                    log(f"Not enough data to calculate EMA for {ticker}")
            except Exception as e:
                log(f"Error calculating EMA for {ticker}: {str(e)}")
                allocation_dict[ticker] = 0  # Default to no allocation in case of error

        # Return target allocation based on the strategy logic
        return TargetAllocation(allocation_dict)