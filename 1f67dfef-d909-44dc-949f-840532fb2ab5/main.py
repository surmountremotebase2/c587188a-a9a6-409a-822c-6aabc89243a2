from surmount.technical_indicators import MACD

# Example OHLCV data for AAPL
# You should replace this with your actual data source
data = {
    "ohlcv": {
        "AAPL": [
            {"close": 150, "open": 145, "high": 155, "low": 144},
            {"close": 152, "open": 150, "high": 158, "low": 149},
            {"close": 155, "open": 152, "high": 160, "low": 150},
            # Add more OHLCV data as needed
        ]
    }
}

# Calculate MACD for AAPL
macd_data = MACD("AAPL", data["ohlcv"]["AAPL"], fast=12, slow=26)

# Print the MACD data and its structure
print("MACD Data for AAPL:")
print(macd_data)

# Print the data structure
print("\nData Structure for AAPL OHLCV:")
print(data["ohlcv"]["AAPL"])import pandas as pd
from surmount.base_class import Strategy, TargetAllocation
from surmount.data import Ratios

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "TSLA"]
        self.investment = 3000  # Total amount to invest

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return [Ratios(ticker) for ticker in self.tickers]

    def calculate_macd(self, data, short_window=12, long_window=26, signal_window=9):
        """Calculate MACD and Signal Line.

        Args:
            data (List[Dict[str, Dict[str, float]]]): OHLCV data.
            short_window (int): Short period for EMA.
            long_window (int): Long period for EMA.
            signal_window (int): Signal period for EMA.

        Returns:
            Tuple[List[float], List[float]]: MACD line and Signal line.
        """
        close_prices = pd.Series([entry['close'] for entry in data])

        # Calculate the short and long EMA
        short_ema = close_prices.ewm(span=short_window, adjust=False).mean()
        long_ema = close_prices.ewm(span=long_window, adjust=False).mean()

        # Calculate MACD line
        macd_line = short_ema - long_ema

        # Calculate Signal line
        signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()

        return macd_line.tolist(), signal_line.tolist()

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Start with no allocation
        ohlcv = data.get("ohlcv")

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