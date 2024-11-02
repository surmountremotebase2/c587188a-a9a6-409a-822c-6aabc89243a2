from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from macd import MACD  # Import the MACD function from the macd module

class TradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META"]
        self.data_list = []

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            closing_prices = [entry[ticker]['close'] for entry in ohlcv]
            macd_line, signal_line = MACD(closing_prices)

            # Example strategy logic based on MACD
            if macd_line and signal_line:
                if macd_line[-1] > signal_line[-1]:  # MACD line crosses above the signal line
                    allocation_dict[ticker] = 1 / len(self.tickers)  # Allocate equally
                elif macd_line[-1] < signal_line[-1]:  # MACD line crosses below the signal line
                    allocation_dict[ticker] = 0  # No allocation

            log(f"{ticker} - MACD: {macd_line[-1]}, Signal: {signal_line[-1]}")

        return TargetAllocation(allocation_dict)