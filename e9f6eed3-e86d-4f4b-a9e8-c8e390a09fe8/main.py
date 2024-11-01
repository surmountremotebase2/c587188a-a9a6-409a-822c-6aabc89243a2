from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL"]
        self.data_list = []
        # Initial budget and share price for buying stocks
        self.budget = 1000
        self.share_price = 0

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
        # Retrieve MACD and signal line values
        macd_data = MACD("AAPL", data["ohlcv"], 12, 26)
        # Print macd_data for debugging
        print(f'MACD Data: {macd_data}')

        if macd_data is None:
            return TargetAllocation({})
        
        macd_line = macd_data["MACD"]
        signal_line = macd_data["signal"]
         # Print macd_line and signal_line for debugging
        print(f'MACD Line: {macd_line}')
        print(f'Signal Line: {signal_line}')
        
        if len(macd_line) < 2 or len(signal_line) < 2:
            return TargetAllocation({})
        
        # Retrieve the current price of AAPL
        current_price = data["ohlcv"][-1]["AAPL"]["close"]
        self.share_price = current_price
        aapl_allocation = 0

        # Check if MACD crosses above the signal line
        if macd_line[-2] < signal_line[-2] and macd_line[-1] > signal_line[-1]:
            log("MACD line crosses above the signal line. Buying signal.")
            # Calculate the fraction of budget to allocate based on current price
            aapl_allocation = min(1, (self.budget / current_price) / current_price)
        
        # Check if MACD crosses below the signal line
        elif macd_line[-2] > signal_line[-2] and macd_line[-1] < signal_line[-1]:
            log("MACD line crosses below the signal line. Selling signal.")
            # Assume selling all held shares
            aapl_allocation = 0
        
        return TargetAllocation({"AAPL": aapl_allocation})