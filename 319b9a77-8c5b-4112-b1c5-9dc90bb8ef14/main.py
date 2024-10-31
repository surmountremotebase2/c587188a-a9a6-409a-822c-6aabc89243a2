from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "TSLA"

    @property
    def assets(self):
        return [self.ticker]

    @property
    def interval(self):
        # Adjust the interval as needed, here using daily data
        return "1day"

    def run(self, data):
        # Get MACD indicator data for TSLA
        macd_data = MACD(self.ticker, data["ohlcv"], fast=12, slow=26)
        
        # Initial target allocation, assuming 0 investment if conditions aren't met
        target_allocation = {self.ticker: 0}  
        
        # Ensure we have enough data points for MACD and Signal line
        if macd_data is not None and len(macd_data["macd"]) > 0 and len(macd_data["signal"]) > 0:
            # Compare the latest MACD line and signal line values
            macd_line = macd_data["macd"][-1]
            signal_line = macd_data["signal"][-1]
            
            # Log for debugging purposes
            log(f"MACD: {macd_line}, Signal: {signal_line}")
            
            # Check if MACD line has crossed above signal line (buy signal)
            if macd_line > signal_line:
                target_allocation[self.ticker] = 1  # Invest in TSLA
            # If MACD line is below signal line, it would maintain or move to 0 allocation (sell signal)
            elif macd_line < signal_line:
                target_allocation[self.ticker] = 0  # Liquidate TSLA position
        
        # Return the appropriate target allocation
        return TargetAllocation(target_allocation)