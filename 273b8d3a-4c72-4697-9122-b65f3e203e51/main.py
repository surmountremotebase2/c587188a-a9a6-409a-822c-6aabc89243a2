from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA

class TradingStrategy(Strategy):
    def __init__(self):
        # Define ticker for the strategy
        self.ticker = "TSLA"
        # Allocation dict to track position for the asset 
        self.allocation_dict = {self.ticker: 0}

    @property
    def interval(self):
        # Use 1-hour interval for the strategy
        return "1hour"

    @property
    def assets(self):
        # Return the list of tickers
        return [self.ticker]

    def run(self, data):
        # Access OHLCV data for TSLA
        ohlcv_data = data["ohlcv"].get(self.ticker, [])
        
        # Ensure we have enough data points for EMA
        if len(ohlcv_data) < 21:
            return TargetAllocation(self.allocation_dict)  # Not enough data to compute EMA

        # Calculate EMA9 and EMA21
        ema9 = EMA(self.ticker, ohlcv_data, period=9)
        ema21 = EMA(self.ticker, ohlcv_data, period=21)

        # Check for crossover signals
        if ema9[-1] > ema21[-1] and ema9[-2] <= ema21[-2]:
            # Enter buy position
            self.allocation_dict[self.ticker] = 1.0  # Allocate full position to TSLA
        elif ema21[-1] > ema9[-1] and ema21[-2] <= ema9[-2]:
            # Liquidate position
            self.allocation_dict[self.ticker] = 0  # No allocation to TSLA
        
        return TargetAllocation(self.allocation_dict)