from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.technical_indicators import EMA

class TradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        self.data_list = []  # Assuming we don't need additional data sources

    @property
    def interval(self):
        return "1hour"  # You can change the interval as needed

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocation
        ohlcv = data.get("ohlcv")  # Get OHLCV data for analysis

        # Ensure enough data for the longest EMA calculation
        if len(ohlcv) < 21:
            return TargetAllocation(allocation_dict)  # Not enough data to make a decision

        # Loop through each ticker to calculate EMAs and generate signals
        for ticker in self.tickers:
            # Calculate EMA 9 and EMA 21
            ema9 = EMA(ticker, ohlcv, length=9)
            ema21 = EMA(ticker, ohlcv, length=21)

            # Check if EMAs have enough data points to evaluate
            if len(ema9) < 2 or len(ema21) < 2:
                continue  # Not enough data to calculate EMAs

            # Log the latest EMA values
            #log(f"Latest {ticker} EMA9: {ema9[-1]}, Latest EMA21: {ema21[-1]}")

            # Entry and exit logic
            if ema9[-1] > ema21[-1] and ema9[-2] <= ema21[-2]:
                # Buy signal: EMA9 crosses above EMA21
                allocation_dict[ticker] = 1.0  # Allocate full position to this ticker
                #log(f"Buy signal generated for {ticker}.")
            elif ema21[-1] > ema9[-1] and ema21[-2] <= ema9[-2]:
                # Sell signal: EMA21 crosses above EMA9
                allocation_dict[ticker] = 0  # Liquidate position
                #log(f"Sell signal generated for {ticker}.")

        return TargetAllocation(allocation_dict)