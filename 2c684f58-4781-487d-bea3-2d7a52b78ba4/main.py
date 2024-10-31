from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers of interest
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD"]

    @property
    def interval(self):
        # Set the data interval to 1 hour as specified
        return "1hour"

    @property
    def assets(self):
        # List the assets for which this strategy is applicable
        return self.tickers

    def run(self, data):
        # Initialize an empty dictionary for allocating funds to tickers
        allocation_dict = {}
        
        # Loop over each ticker to evaluate the strategy criteria
        for ticker in self.tickers:
            # Retrieve technical indicators for each ticker
            ema9 = EMA(ticker, data["ohlcv"], 9)
            ema21 = EMA(ticker, data["ohlcv"], 21)
            rsi = RSI(ticker, data["ohlcv"], 4)
            macd = MACD(ticker, data["ohlcv"], 12, 26)
            
            # Check if enough data is available to compute indicators
            if ema9 is not None and ema21 is not None and rsi is not None and macd is not None:
                # Determine if investment criteria are met
                if ema9[-1] > ema21[-1] and rsi[-1] > 65 and macd["MACD"][-1] > macd["signal"][-1]:
                    # Criteria for buying
                    allocation_dict[ticker] = 1.0 / len(self.tickers)  # Equal allocation considering $500 total
                elif ema9[-1] < ema21[-1] and (rsi[-1] < 45 and macd["MACD"][-1] < macd["signal"][-1]):
                    # Criteria for selling or liquidating
                    allocation_dict[ticker] = 0  # No allocation, i.e., sell/liquidate
                else:
                    # Hold criteria or no change in position
                    allocation_dict[ticker] = 0  # No allocation in uncertainty, for simplicity
            else:
                # If data is not sufficient to calculate indicators, skip allocation for this ticker
                allocation_dict[ticker] = 0

        # Log the allocation decision
        log(str(allocation_dict))
        
        # Return the allocation dict encapsulated in a TargetAllocation object
        return TargetAllocation(allocation_dict)