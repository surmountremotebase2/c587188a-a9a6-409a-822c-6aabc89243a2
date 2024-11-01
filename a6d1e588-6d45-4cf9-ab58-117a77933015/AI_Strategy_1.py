from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):

    @property
    def assets(self):
        # List of assets the strategy will trade.
        return ["AAPL"]

    @property
    def interval(self):
        # The time interval at which the strategy will operate, e.g., "1day" for daily intervals.
        return "1day"

    def run(self, data):
        # The main method to implement the trading logic.
        
        # Initial allocation with 0% of the portfolio to AAPL,
        # indicating no position initially until conditions are met.
        apple_stake = 0 

        # Using the MACD technical indicator for AAPL.
        # Parameters are: ticker, data, fast period, slow period.
        # Default parameters of 12, 26 are commonly used for MACD.
        macd_result = MACD("AAPL", data["ohlcv"], fast=12, slow=26)

        # MACD consists of the MACD line, Signal line, and Histogram. 
        # We're interested in the MACD line (macd) and the signal line (signal) for crossovers.
        macd_line = macd_result["MACD"]
        signal_line = macd_result["signal"]

        # Check to ensure we have enough data for both MACD and Signal lines.
        if len(macd_line) > 0 and len(signal_line) > 0:
            # MACD strategy: Buy signal - when MACD crosses above Signal line.
            if macd_line[-1] > signal_line[-1] and macd_line[-2] < signal_line[-2]:
                log("MACD crossover bullish signal detected: Buying AAPL")
                apple_stake = 1  # 100% allocation to AAPL.
                
            # Sell signal (can also be a short signal in different contexts) -
            # when MACD crosses below the Signal line.
            elif macd_line[-1] < signal_line[-1] and macd_line[-2] > signal_line[-2]:
                log("MACD crossover bearish signal detected: Selling AAPL")
                apple_stake = 0  # 0% allocation to AAPL signifies selling off or not holding the asset.
        else:
            # If there's not enough data, log a message and take no action.
            log("Not enough data for MACD calculation.")

        # Return the target allocation as a dictionary where the key is the asset symbol
        # (AAPL in this case) and the value is the target allocation percentage.
        return TargetAllocation({"AAPL": apple_stake})