from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.asset = "AAPL"  # Target asset for the strategy

    @property
    def assets(self):
        return [self.asset]

    @property
    def interval(self):
        return "1hour"  # Interval for the trading data

    def calculate_macd_and_signal(self, ohlcv):
        # Calculate the 12-day and 26-day EMAs
        ema12 = EMA("close", ohlcv, 12)
        ema26 = EMA("close", ohlcv, 26)

        # Compute the MACD line (difference between EMA12 and EMA26)
        macd_line = [ema12[i] - ema26[i] for i in range(len(ema26))]

        # Calculate the Signal line (9-day EMA of the MACD line)
        signal_line = EMA(macd_line, ohlcv, 9)

        return macd_line, signal_line

    def run(self, data):
        allocation = 0  # Default allocation (fully liquidate position)

        # Retrieve historical OHLCV and indicator data for asset
        ohlcv = data["ohlcv"]
        ema9 = EMA(self.asset, ohlcv, length=9)
        ema21 = EMA(self.asset, ohlcv, length=21)
        ema12 = EMA(self.asset, ohlcv, length=12)
        ema26 = EMA(self.asset, ohlcv, length=26)
        rsi4 = RSI(self.asset, ohlcv, length=4)
        macd_line, signal_line = self.calculate_macd_and_signal(ohlcv)


        if not all([ema9, ema21, rsi4, macd, ema9_macd]):
            log("Insufficient data for indicators.")
            return TargetAllocation({self.asset: allocation})

        # Current indicators
        current_ema9 = ema9[-1]
        current_ema21 = ema21[-1]
        current_rsi4 = rsi4[-1]

        # Trading signals
        enter_signal = current_ema9 > current_ema21 and current_rsi4 > 65 and macd_line > signal_line
        exit_signal = current_ema9 < current_ema21 or current_rsi4 < 45 or macd_line < signal_line

        # Determine allocation based on trading signals
        if enter_signal:
            log("Entering position: EMA9 above EMA21, RSI(4) > 65, MACD line > 9-days EMA of MACD.")
            allocation = 1  # Invest 100% of the portfolio
        elif exit_signal:
            log("Exiting position: EMA9 crosses below EMA21, RSI(4) < 45, or MACD line < 9-days EMA of MACD.")
            allocation = 0  # Liquidate position

        return TargetAllocation({self.asset: allocation})