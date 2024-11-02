import pandas as pd
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "TSLA"]
        self.investment = 3000  # Total amount to invest

    @property
    def interval(self):
        return "1day"  # Define the interval for the strategy

    @property
    def assets(self):
        return self.tickers  # Define the assets you are trading

    def calculate_macd(self, data, short_window=12, long_window=26, signal_window=9):
        """Calculate the MACD and Signal line."""
        short_ema = data['close'].ewm(span=short_window, adjust=False).mean()
        long_ema = data['close'].ewm(span=long_window, adjust=False).mean()
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
        return macd_line.tolist(), signal_line.tolist()

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Start with no allocation
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            # Ensure OHLCV data is available for the ticker
            if ticker not in ohlcv:
                continue
            
            macd_line, signal_line = self.calculate_macd(ohlcv[ticker])  # Get MACD and Signal lines

            # Ensure enough data is available
            if len(macd_line) < 2 or len(signal_line) < 2:
                continue  # Not enough data to make a decision

            # Buy condition: MACD crosses above the Signal line
            if macd_line[-2] < signal_line[-2] and macd_line[-1] > signal_line[-1]:
                allocation_dict[ticker] = self.investment / len(self.tickers)  # Allocate investment

            # Sell condition: Signal line crosses above the MACD
            elif macd_line[-2] > signal_line[-2] and macd_line[-1] < signal_line[-1]:
                allocation_dict[ticker] = 0  # Liquidate the position

        return TargetAllocation(allocation_dict)  # Return the allocation