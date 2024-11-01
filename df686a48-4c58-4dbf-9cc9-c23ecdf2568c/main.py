#Type code here
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD

class AAPLTradingStrategy(Strategy):
    @property
    def interval(self):
        return "1h"  # 1-hour interval for the strategy

    @property
    def assets(self):
        return ["AAPL"]  # Only trading AAPL

    def run(self, data):
        allocations = {}
        capital_per_trade = 1000  # Fixed amount to invest

        # Get the OHLCV data for AAPL
        ohlcv = data.get("ohlcv")["AAPL"]

        # Calculate EMAs
        ema9 = EMA("close", ohlcv, 9)
        ema21 = EMA("close", ohlcv, 21)
        ema12 = EMA("close", ohlcv, 12)
        ema26 = EMA("close", ohlcv, 26)

        # Calculate MACD Line and Signal Line
        macd_line, signal_line = MACD("close", ohlcv, 12, 26, 9)

        # Calculate RSI with a 4-period
        rsi = RSI("close", ohlcv, 4)

        # Entry Condition: EMA9 > EMA21, RSI > 65, and MACD line > Signal line
        if ema9[-1] > ema21[-1] and rsi[-1] > 65 and macd_line[-1] > signal_line[-1]:
            allocations["AAPL"] = capital_per_trade  # Invest $1000 in AAPL

        # Exit Condition: EMA9 < EMA21, RSI < 45, and MACD line < Signal line
        elif ema9[-1] < ema21[-1] and rsi[-1] < 45 and macd_line[-1] < signal_line[-1]:
            allocations["AAPL"] = 0  # Liquidate the position

        return TargetAllocation(allocations)