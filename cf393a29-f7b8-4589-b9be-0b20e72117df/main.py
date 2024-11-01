from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "AAPL"

    @property
    def assets(self):
        return [self.ticker]

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        aapl_data = data["ohlcv"]

        # Calculate indicators: EMA9, EMA21, RSI(4), and MACD(12,26)
        ema9 = EMA(self.ticker, aapl_data, 9)
        ema21 = EMA(self.ticker, aapl_data, 21)
        rsi = RSI(self.ticker, aapl_data, 4)
        macd_data = MACD(self.ticker, aapl_data, 12, 26)
        macd_line = macd_data["MACD"]
        signal_line = macd_data["signal"]
        histogram = [m - s for m, s in zip(macd_line, signal_line)]

        # Initialize AAPL stake
        aapl_stake = 0

        if len(ema9) > 0 and len(ema21) > 0 and len(rsi) > 0 and len(histogram) > 0:
            # Condition to open a position: EMA9 > EMA21, RSI > 65, and MACD line above signal line (bullish momentum)
            if ema9[-1] > ema21[-1] and rsi[-1] > 65 and histogram[-1] > 0:
                aapl_stake = 1  # Full investment in AAPL
                log("Buying signal: EMA9 > EMA21, RSI > 65, and MACD histogram is positive")
            # Condition to liquidate a position: EMA9 crosses below EMA21, RSI < 45, and MACD line below signal line (bearish momentum)
            elif ema9[-1] < ema21[-1] and rsi[-1] < 45 and histogram[-1] < 0:
                aapl_stake = 0  # Liquidate AAPL position
                log("Selling signal: EMA9 < EMA21, RSI < 45, and MACD histogram is negative")

        return TargetAllocation({self.ticker: aapl_stake})