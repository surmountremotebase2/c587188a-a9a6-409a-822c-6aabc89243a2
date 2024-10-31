from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD_F
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Initialize with a single asset, for example, AAPL
        self.tickers = ["AAPL"]
    
    @property
    def assets(self):
        # The assets that this strategy will analyze
        return self.tickers

    @property
    def interval(self):
        # Use daily data for MACD calculation
        return "1day"
    
    def run(self, data):
        # Extract closing prices for the asset
        ticker = self.tickers[0]  # In case of multiple assets, handle accordingly
        ohlcv_data = data["ohlcv"]

        # Calculate MACD and Signal line
        macd_data = MACD_F(ticker=ticker, data=ohlcv_data, fast=12, slow=26)
        macd_line = macd_data["MACD"]
        signal_line = macd_data["signal"]

        # Default to no allocation
        allocation = 0

        if len(macd_line) > 0 and len(signal_line) > 0:
            # Check for MACD cross above the Signal line for Buy signal
            if macd_line[-2] < signal_line[-2] and macd_line[-1] > signal_line[-1]:
                log("MACD crossover bullish signal detected.")
                allocation = 1  # Allocate fully
            # Check for MACD cross below the Signal line for Sell signal
            elif macd_line[-2] > signal_line[-2] and macd_line[-1] < signal_line[-1]:
                log("MACD crossover bearish signal detected.")
                allocation = 0  # Allocate nothing

        # Return the target allocation for AAPL based on MACD signal
        return TargetAllocation({ticker: allocation})