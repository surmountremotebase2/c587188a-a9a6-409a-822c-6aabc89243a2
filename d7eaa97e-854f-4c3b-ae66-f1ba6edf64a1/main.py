from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers to be traded
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        
        # Initialize variables to keep track of the allocation
        self.allocation = {ticker: 0 for ticker in self.tickers}

    @property
    def assets(self):
        # The assets that we are interested in
        return self.tickers

    @property
    def interval(self):
        # Use 1-hour interval for MACD calculation
        return "1hour"

    def run(self, data):
        # Iterate through each ticker to calculate the MACD and decide on the allocation
        for ticker in self.tickers:
            # Calculate MACD using the surmount library function
            macd_data = MACD(ticker, data, fast=12, slow=26)
            # Log the MACD data structure for debugging
            log(f"MACD data for {ticker}: {macd_data}")
            
            # Check if the MACD data has the necessary keys
            if macd_data is not None and "MACD" in macd_data and "signal" in macd_data:
                macd_line = macd_data["MACD"][-1]
                signal_line = macd_data["signal"][-1]

                log(f"MACD data for {ticker}: {macd_line}")
                log(f"MACD data for {ticker}: {singal_line}")

                # Decision to invest or liquidate
                if macd_line > signal_line:
                    self.allocation[ticker] = 1.0 / len(self.tickers)  # Invest equally among the tickers
                else:
                    self.allocation[ticker] = 0  # Liquidate
            else:
                log(f"MACD data is missing keys for {ticker}, keeping previous allocation.")

        # Return the target allocation based on the MACD strategy
        return TargetAllocation(self.allocation)