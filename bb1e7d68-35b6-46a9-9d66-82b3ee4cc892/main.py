from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker symbol for the asset you want to trade
        self.ticker = "TSLA"

    @property
    def assets(self):
        # Return a list containing the ticker of the asset(s) being traded
        return [self.ticker]

    @property
    def interval(self):
        # Define the data interval for the strategy. Choices are: 1min, 5min, 1hour, 4hour, 1day
        # For MACD, typically, '1day' or '1hour' are used, depending on how frequently you want to trade.
        return "1day"

    def run(self, data):
        # The 'data' parameter contains historical data needed for computing technical indicators.

        # Calculate the MACD and its signal line for the asset.
        # Adjust the fast, slow, and signal periods as needed.
        macd_data = MACD(self.ticker, data["ohlcv"], fast=12, slow=26, signal=9)

        # Initialize allocation assuming no position to start with.
        tsla_stake = 0  # 0% allocation

        if macd_data is not None and len(macd_data["MACD"]) > 1:
            # Check if the MACD line crossed above the signal line
            if macd_data["MACD"][-2] < macd_data["signal"][-2] and macd_data["MACD"][-1] > macd_data["signal"][-1]:
                log("MACD line crossed above the signal line. Buying TSLA.")
                tsla_stake = 1  # 100% allocation
            # Check if the MACD line crossed below the signal line
            elif macd_data["MACD"][-2] > macd_data["signal"][-2] and macd_data["MACD"][-1] < macd_data["signal"][-1]:
                log("MACD line crossed below the signal line. Liquidating TSLA position.")
                tsla_stake = 0  # 0% allocation

        # Return the target allocation object with the desired stake in TSLA
        return TargetAllocation({self.ticker: tsla_stake})