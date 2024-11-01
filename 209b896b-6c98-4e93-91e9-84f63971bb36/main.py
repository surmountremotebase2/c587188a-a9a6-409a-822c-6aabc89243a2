from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define AAPL as the target asset for this strategy
        self.ticker = "AAPL"

    @property
    def assets(self):
        # Indicate that this strategy is intended for AAPL
        return [self.ticker]

    @property
    def interval(self):
        # Utilize daily data for MACD calculation
        return "1day"

    def run(self, data):
        # Initialize AAPL stake to zero
        allocation_dict = {self.ticker: 0}

        # Calculate MACD for AAPL
        macd_data = MACD(self.ticker, data["ohlcv"], fast=12, slow=26)

        # Check if macd_data is valid and contains necessary keys
        macd_line = macd_data.get("MACD")
        signal_line = macd_data.get("signal")

        if macd_line is None or signal_line is None or len(macd_line) < 2:
            # Not enough data to calculate MACD
            log("Not enough data to calculate MACD.")
            return TargetAllocation(allocation_dict)

        # Compare the last two MACD values to detect crossover
        if macd_line[-1] > signal_line[-1] and macd_line[-2] < signal_line[-2]:
            # MACD crosses above signal line - bullish signal
            allocation_dict[self.ticker] = 1.0  # Full investment
        elif macd_line[-1] < signal_line[-1] and macd_line[-2] > signal_line[-2]:
            # MACD crosses below signal line - bearish signal
            allocation_dict[self.ticker] = 0  # Exit position

        # Log the action taken
        log(f'Allocation for {self.ticker}: {allocation_dict[self.ticker]}')

        return TargetAllocation(allocation_dict)