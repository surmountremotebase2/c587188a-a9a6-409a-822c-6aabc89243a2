from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA  # Importing Simple Moving Average Indicator
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "AAPL"  # Target asset for the strategy
        
        # No additional data_list required for moving averages as they are calculated from the ohlcv data
        self.data_list = []

    @property
    def interval(self):
        return "1day"  # Defines the interval for data collection

    @property
    def assets(self):
        return [self.ticker]  # Assets to be included in the strategy

    @property
    def data(self):
        return self.data_list  # Data requirements for the strategy

    def run(self, data):
        # Fetching the OHLCV data for AAPL
        ohlcv_data = data["ohlcv"]
        
        # Check to ensure there's enough data for calculating the moving averages
        if len(ohlcv_data) < max(short_term_period, long_term_period):
            log("Not enough data to calculate the moving averages.")
            return TargetAllocation({self.ticker: 0})  # No action, return 0 allocation

        # Calculating short-term and long-term moving averages
        short_term_period = 10  # Define the short term period
        long_term_period = 30  # Define the long term period
        
        short_ma = SMA(self.ticker, ohlcv_data, short_term_period)
        long_ma = SMA(self.ticker, ohlcv_data, long_term_period)

        # Checking the crossover condition to make trading decisions
        if short_ma[-1] > long_ma[-1]:  # If short-term MA crosses above long-term MA
            allocation = 1  # Buy signal (100% allocation)
            log("Short-term MA has crossed above the long-term MA. Buying AAPL.")
        elif short_ma[-1] < long_ma[-1]:  # If short-term MA crosses below long-term MA
            allocation = 0  # Sell signal (0% allocation)
            log("Short-term MA has crossed below the long-term MA. Selling AAPL.")
        else:
            allocation = 0  # Default action is to not hold the asset
            log("No MA crossover observed. Keeping allocation at 0.")

        return TargetAllocation({self.ticker: allocation})