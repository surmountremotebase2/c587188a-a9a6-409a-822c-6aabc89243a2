from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Specify the ticker for Apple
        self.ticker = "AAPL"
    
    @property
    def assets(self):
        # We're only interested in Apple for this strategy
        return [self.ticker]
    
    @property
    def interval(self):
        # Choose an interval for the data, '1day' for daily data
        return "1day"

    def run(self, data):
        # Initialize allocation to 0
        allocation = {self.ticker: 0.0}

        # Check if we have enough data
        if len(data["ohlcv"]) > 14: # Assuming we want at least 14 periods for RSI calculation
            # Calculate the 26-period EMA for AAPL
            ema_values = EMA(self.ticker, data["ohlcv"], length=26)
            # Calculate the 14-period RSI for AAPL
            rsi_values = RSI(self.ticker, data["ohlcv"], length=14)
            
            if ema_values and rsi_values: # Ensure we have both EMA and RSI values
                # Compare the last close to the EMA and check if RSI is below 70
                last_close = data["ohlcv"][-1][self.ticker]["close"]
                last_ema = ema_values[-1]
                last_rsi = rsi_values[-1]

                if last_close > last_ema and last_rsi < 70:
                    # Conditions met, signal to buy (allocate 100% of capital to AAPL)
                    allocation[self.ticker] = 1.0
                    
                # For logging purposes
                log(f"Last Close: {last_close}, Last EMA: {last_ema}, Last RSI: {last_rsi}")

        # Return the allocation desired based on our logic
        return TargetAllocation(allocation)