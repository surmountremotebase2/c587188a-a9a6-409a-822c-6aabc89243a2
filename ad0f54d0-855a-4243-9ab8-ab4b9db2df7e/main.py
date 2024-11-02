from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define tickers for the strategy
        self.tickers = ["TSLA", "AAPL", "MSFT"]
        # Allocation dict to track our position for each asset 
        self.allocation_dict = {i: 0 for i in self.tickers}

    @property
    def interval(self):
        # Use 1-hour interval for the strategy
        return "1hour"

    @property
    def assets(self):
        # Return the list of tickers
        return self.tickers

    def run(self, data):
        # Iterate through tickers to apply the strategy
        for ticker in self.tickers:
            macd_data = MACD(ticker, data["ohlcv"], fast=12, slow=26)
            
            # Ensure we have enough data points for MACD and signal line
            if macd_data and 'macd' in macd_data and 'signal' in macd_data:
                if len(macd_data["macd"]) > 1 and len(macd_data["signal"]) > 1:
                    macd_line = macd_data["macd"][-1]  # Latest MACD value
                    signal_line = macd_data["signal"][-1]  # Latest Signal value
                    prev_macd_line = macd_data["macd"][-2]  # Previous MACD value
                    prev_signal_line = macd_data["signal"][-2]  # Previous Signal value

                    # Check for MACD line crossing above signal line (buy signal)
                    if macd_line > signal_line and prev_macd_line <= prev_signal_line:
                        log(f"Buy signal for {ticker}")
                        self.allocation_dict[ticker] = 1.0 / len(self.tickers)  # Allocate equally among assets

                    # Liquidate position when signal line crosses above MACD line
                    elif signal_line > macd_line and prev_signal_line <= prev_macd_line:
                        log(f"Liquidate position for {ticker}")
                        self.allocation_dict[ticker] = 0

                    # Maintain current position if no crossover
                    else:
                        log(f"No crossover for {ticker}, maintaining position.")
                else:
                    log(f"Not enough data points for MACD calculation for {ticker}.")
            else:
                log(f"No valid MACD data for {ticker}. Possible causes: insufficient data or incorrect data format.")

        return TargetAllocation(self.allocation_dict)

def log(message):
    print(message)  # Replace this with a logging framework as needed