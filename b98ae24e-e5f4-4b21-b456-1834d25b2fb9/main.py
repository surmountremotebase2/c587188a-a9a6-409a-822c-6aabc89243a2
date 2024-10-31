from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):

    @property
    def assets(self):
        # Define the assets you are interested in
        return ["AAPL"]

    @property
    def interval(self):
        # Define the interval for data fetching
        return "1day"

    def run(self, data):
        # Only consider the asset defined in assets property
        ticker = self.assets[0]
        
        # Calculate MACD using predefined technical indicators
        macd_data = MACD(ticker=ticker, data=data["ohlcv"], fast=12, slow=26, signal=9)
        
        if macd_data is None or len(macd_data['MACD']) < 2:
            # Insufficient data to compute MACD
            return TargetAllocation({})
        
        # Current and previous MACD and signal line values
        current_macd = macd_data['MACD'][-1]
        previous_macd = macd_data['MACD'][-2]
        current_signal = macd_data['signal'][-1]
        previous_signal = macd_data['signal'][-2]
        
        if current_macd > current_signal and previous_macd <= previous_signal:
            # MACD line crosses above the signal line - Buy signal
            log("Buying signal detected for {}".format(ticker))
            allocation = 1  # Max allocation
        elif current_macd < current_signal and previous_macd >= previous_signal:
            # MACD line crosses below the signal line - Sell signal
            log("Selling signal detected for {}".format(ticker))
            allocation = 0  # No allocation
        else:
            # No clear signal, maintain current allocation
            log("No clear buy or sell signal for {}".format(ticker))
            allocation = 0.5  # Neutral allocation
        
        # Return the target allocation as per the signal detected
        return TargetAllocation({ticker: allocation})