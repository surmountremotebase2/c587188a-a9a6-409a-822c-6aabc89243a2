from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the asset we are trading
        self.ticker = "AAPL"
        
        # Initializing data_list despite only requiring technical indicators
        # as OHLCV data is fetched based on assets and not explicitly listed here
        self.data_list = []

    @property
    def interval(self):
        # Setting the interval for our historical data analysis
        return "1day"

    @property
    def assets(self):
        # Specifying the asset(s) we're interested in
        return [self.ticker]

    def run(self, data):
        # Fetch the EMA data for our asset
        ema9 = EMA(self.ticker, data["ohlcv"], 9)
        ema21 = EMA(self.ticker, data["ohlcv"], 21)
        
        # Check if both EMAs have at least one data point
        if len(ema9) > 0 and len(ema21) > 0:
            # Compare the last (most recent) EMA values
            ema9_last = ema9[-1]
            ema21_last = ema21[-1]
            
            # Logic to determine buy or sell
            # If EMA9 crosses above EMA21, consider it a buy signal
            if ema9_last > ema21_last:
                allocation = {"AAPL": 1.0}  # Fully allocate to AAPL
                
            # If EMA9 crosses below EMA21, consider it a sell signal, thus invest in cash (or equivalent)
            elif ema9_last < ema21_last:
                allocation = {"AAPL": 0.0}  # Fully divest from AAPL
                
            # If there's no clear signal, maintain existing allocation
            else:
                allocation = {"AAPL": 0.5}  # Neutral stance, example allocation

        # If EMA data is insufficient, suggest a default or safe allocation
        else:
            allocation = {"AAPL": 0.5}  # Neutral stance, example allocation
            
        # Returning our target allocation based on signals
        return TargetAllocation(allocation)