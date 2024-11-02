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
            if macd_data and len(macd_data["MACD"]) > 0 and len(macd_data["signal"]) > 0:
                macd_line = macd_data["MACD"][-1]
                signal_line = macd_data["signal"][-1]
                prev_macd_line = macd_data["MACD"][-2]
                prev_signal_line = macd_data["signal"][-2]
                
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

        return TargetAllocation(self.allocation_dict)