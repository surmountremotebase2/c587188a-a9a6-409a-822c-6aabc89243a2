from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, Slope, SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL"]  # Example for Apple Inc., but can be used for any listed tickers

    @property
    def interval(self):
        return "1day"  # Daily intervals for the indicators

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        # No extra data needed here, the indicators will be calculated from OHLCV data
        return []

    def run(self, data):
        # Initialize a zero allocation for tickers
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        
        for ticker in self.tickers:
            ohlcv_data = data['ohlcv'][-20:]  # Getting last 20 days of data for calculations

            # Calculate MACD
            macd_values = MACD(ticker=ticker, data=ohlcv_data, fast=12, slow=26)['MACD'][-1]  # Last value of MACD

            # Calculate slope of the 10-day SMA
            sma_values = SMA(ticker=ticker, data=ohlcv_data, length=10)
            slope_value = Slope(ticker=ticker, data=[{'close': value} for value in sma_values], length=5)[-1]  # Last value of the slope over SMA10

            # Trading logic
            if macd_values > 0 and slope_value > 0:
                # Positive momentum and upward slope, allocate 100% to this ticker
                allocation_dict[ticker] = 1
            # No need to explicitly handle negative case, as allocation starts at 0

        return TargetAllocation(allocation_dict)