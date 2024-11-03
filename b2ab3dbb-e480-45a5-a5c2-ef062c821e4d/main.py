#Type code here
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX"]

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            try:
                # Calculate RSI
                rsi = RSI(ticker, ohlcv, length=4)[-1]

                # Check buy condition: RSI(4) greater than 65
                if rsi > 65:
                    allocation_dict[ticker] = 1/ len(self.tickers)

                # Check sell condition: RSI(4) falls below 45
                elif rsi < 45:
                    allocation_dict[ticker] = 0

            except Exception:
                # Handle exceptions silently
                pass

        return TargetAllocation(allocation_dict)