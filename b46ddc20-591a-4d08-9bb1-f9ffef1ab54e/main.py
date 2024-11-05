from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import Momentum, Slope
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers we're interested in
        self.tickers = ["AAPL", "GOOGL", "NVDA"]
        # Momentum calculation period
        self.momentum_period = 10
        # SMA calculation for the slope
        self.sma_period = 10
        
    @property
    def assets(self):
        # We trade these assets
        return self.tickers

    @property
    def interval(self):
        # Use daily data
        return "1day"

    def run(self, data):
        # Dictionary to store the target allocation for each asset
        allocation_dict = {}
        
        for ticker in self.tickers:
            # Calculate momentum
            momentum = Momentum(ticker, data["ohlcv"], self.momentum_period)
            # Calculate the slope of the SMA
            sma_slope = Slope(ticker, data["ohlcv"], self.sma_period)
            
            # Check if we have sufficient data to make a decision
            if momentum is not None and sma_slope is not None:
                # Check if both momentum and SMA slope are positive
                if momentum[-1] > 0 and sma_slope[-1] > 0:
                    # Set allocation to equally divide capital among chosen assets
                    allocation_dict[ticker] = 1.0 / len(self.tickers)
                else:
                    # If conditions are not met, do not allocate any capital to this asset
                    allocation_dict[ticker] = 0.0
            else:
                # In case of insufficient data, avoid trading this asset
                allocation_dict[ticker] = 0.0
        
        # Return the target allocation
        return TargetAllocation(allocation_dict)