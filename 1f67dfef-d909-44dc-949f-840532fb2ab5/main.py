import pandas as pd
from surmount.base_class import Strategy, TargetAllocation
from surmount.data import Ratios

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "TSLA"]
        self.investment = 3000  # Total amount to invest

    # Other methods as before...

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Start with no allocation
        ohlcv = data.get("ohlcv")

        # Example print statement (make sure to remove or modify for production)
        print(data["ohlcv"]["AAPL"])  # Ensure this line is not mixed with import statements

        for ticker in self.tickers:
            macd_line, signal_line = self.calculate_macd(ohlcv[ticker])  # Get MACD and Signal lines

            # Check for MACD crossover conditions
            if len(macd_line) < 2 or len(signal_line) < 2:
                continue  # Not enough data to make a decision

            # Buy condition: MACD crosses above the Signal line
            if macd_line[-2] < signal_line[-2] and macd_line[-1] > signal_line[-1]:
                allocation_dict[ticker] = self.investment / len(self.tickers)  # Allocate investment

            # Sell condition: Signal line crosses above the MACD
            elif macd_line[-2] > signal_line[-2] and macd_line[-1] < signal_line[-1]:
                allocation_dict[ticker] = 0  # Liquidate the position

        return TargetAllocation(allocation_dict)  # Return the allocation