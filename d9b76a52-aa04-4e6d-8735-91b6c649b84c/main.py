from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers that we will be trading
        self.tickers = ["AAPL", "MSFT", "WMT", "JPM", "NVDA", "AMD", "META", "TSLA",
                        "AMZN", "GOOGL", "LMT", "NOC", "GC", "BAC", "GS", "PFE", "JNJ", "FDX", "UNP"]
        # Define a placeholder for RSI period
        self.rsi_period = 14

    @property
    def assets(self):
        # Specifies the assets this strategy is interested in
        return self.tickers

    @property
    def interval(self):
        # Specifies the data interval. 1 day is a common choice for RSI-based strategies.
        return "1day"

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            rsi_values = RSI(ticker, data["ohlcv"], self.rsi_period)
            if not rsi_values or len(rsi_values) < self.rsi_period: # Ensuring we have enough data points
                continue # Skip this iteration if RSI values are not available or insufficient
            current_rsi = rsi_values[-1]
            if current_rsi < 30:
                # RSI below 30 suggests that the asset is oversold, consider buying
                allocation_dict[ticker] = 1.0 / len(self.tickers)
            elif current_rsi > 70:
                # RSI above 70 suggests that the asset is overbought, consider selling
                # In this strategy framework, setting allocation to 0 implies selling off the position
                allocation_dict[ticker] = 0
            else:
                # If RSI is between 30 and 70, keep or do not change the allocation
                # Here not changing means we do not include the ticker in allocation_dict
                # Or you can explicitly manage holdings based on your strategy rules
                pass

        return TargetAllocation(allocation_dict)