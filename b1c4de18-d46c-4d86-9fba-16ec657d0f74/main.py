from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Initialize with the ticker for Apple Inc.
        self.ticker = "AAPL"
    
    @property
    def assets(self):
        # Define the trading asset
        return [self.ticker]
    
    @property
    def interval(self):
        # Set the interval for data collection
        return "1hour"
    
    def run(self, data):
        # Extract the OHLCV (Open/High/Low/Close/Volume) data for calculations
        ohlcv_data = data["ohlcv"]
        
        # Calculate EMAs
        ema9 = EMA(self.ticker, ohlcv_data, 9)
        ema21 = EMA(self.ticker, ohlcv_data, 21)
        ema12 = EMA(self.ticker, ohlcv_data, 12)
        ema26 = EMA(self.ticker, ohlcv_data, 26)
        
        # Calculate the RSI
        rsi = RSI(self.ticker, ohlcv_data, 4)
        
        # Calculate MACD values
        macd_values = MACD(self.ticker, ohlcv_data, fast=12, slow=26)
        macd_line = macd_values["MACD"]
        signal_line = macd_values["signal"]
        
        # Determine the trading action based on strategy conditions
        aapl_stake = 0
        if len(ema9) > 0 and len(ema21) > 0:
            # Check for the buying conditions
            if ema9[-1] > ema21[-1] and rsi[-1] > 65 and macd_line[-1] > signal_line[-1]:
                log("Buying conditions met - Investing in AAPL")
                aapl_stake = 1  # Invest in AAPL
                
            # Check for the selling conditions
            elif ema9[-1] < ema21[-1] and rsi[-1] < 45 and macd_line[-1] < signal_line[-1]:
                log("Selling conditions met - Liquidating AAPL position")
                aapl_stake = 0  # Liquidate AAPL position
        
        return TargetAllocation({self.ticker: aapl_stake})
# Unable to generate strategy