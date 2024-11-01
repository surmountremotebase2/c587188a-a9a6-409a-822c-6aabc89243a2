from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker symbol you want to trade.
        self.ticker = "AAPL"
    
    @property
    def assets(self):
        # List of assets this strategy will trade.
        return [self.ticker]

    @property
    def interval(self):
        # Choose an appropriate interval for data (1min, 5min, 1hour, 4hour, 1day)
        return "1day"

    def run(self, data):
        # Initialize the target allocation for the asset to 0.
        allocation = {self.ticker: 0}
        
        # Calculate MACD using the closing prices of the asset.
        # The fast, slow, and signal periods are set to common defaults: 12, 26, and 9 respectively.
        macd_dict = MACD(self.ticker, data["ohlcv"], fast=12, slow=26, signal=9)
        
        if macd_dict:
            # Get the MACD line and the signal line.
            macd_line = macd_dict["MACD"]
            signal_line = macd_dict["signal"]
            
            if len(macd_line) > 1 and len(signal_line) > 1:
                # Check if MACD line crossed above the signal line for a buy signal.
                if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
                    log(f"Buying {self.ticker}")
                    allocation[self.ticker] = 1  # Set allocation to 100%
                # Check if MACD line crossed below the signal line for a sell/exit signal.
                elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
                    log(f"Selling {self.ticker}")
                    allocation[self.ticker] = 0  # Set allocation to 0%
                else:
                    log(f"Holding {self.ticker}")
            else:
                log("Insufficient data for MACD calculation.")
        else:
            log("MACD calculation failed.")

        return TargetAllocation(allocation)