from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL"]

    @property
    def interval(self):
        # setting the interval to 1hour as requested
        return "1hour"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        # Initializing allocation for AAPL to 0
        aapl_stake = 0

        # Calculate EMA9 and EMA21 for AAPL
        ema9 = EMA("AAPL", data["ohlcv"], 9)
        ema21 = EMA("AAPL", data["ohlcv"], 21)

        # Calculate MACD (with default parameters equivalent to (12,26))
        macd_result = MACD("AAPL", data["ohlcv"], fast=12, slow=26)
        macd_line = macd_result["MACD"]
        signal_line = macd_result["signal"]

        # Calculate RSI with a period of 4
        rsi = RSI("AAPL", data["ohlcv"], 4)

        # Check if enough data
        if len(ema9) > 0 and len(ema21) > 0 and len(macd_line) > 0 and len(signal_line) > 0 and len(rsi) > 0:
            # Conditions to enter trade
            if ema9[-1] > ema21[-1] and rsi[-1] > 65 and macd_line[-1] > signal_line[-1]:
                aapl_stake = 1  # Setting allocation to 100% of the portfolio for AAPL

            # Conditions to exit trade
            elif ema9[-1] < ema21[-1] and rsi[-1] < 45 and macd_line[-1] < signal_line[-1]:
                aapl_stake = 0  # Liquidating position by setting allocation back to 0

        return TargetAllocation({"AAPL": aapl_stake})