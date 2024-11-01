from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL"]

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        # Initialize AAPL stake
        allocation_dict = {"AAPL": 0}

        # Accessing EMA9, EMA21, RSI, and MACD for AAPL
        ema9 = EMA("AAPL", data["ohlcv"], length=9)
        ema21 = EMA("AAPL", data["ohlcv"], length=21)
        rsi = RSI("AAPL", data["ohlcv"], length=4)
        macd = MACD("AAPL", data["ohlcv"], fast=12, slow=26)

        if not ema9 or not ema21 or not rsi or not macd:
            log("Required indicators not available.")
            return TargetAllocation(allocation_dict)

        # Check if data has enough points
        if len(ema9) > 1 and len(ema21) > 1 and len(rsi) > 1:
            current_ema9 = ema9[-1]
            current_ema21 = ema21[-1]
            current_rsi = rsi[-1]
            current_macd = macd["MACD"][-1] if "MACD" in macd else None
            macd_signal = macd["signal"][-1] if "signal" in macd else None

            # Buy Logic: EMA9 above EMA21, RSI above 65, and MACD above signal line
            if current_ema9 > current_ema21 and current_rsi > 65 and current_macd is not None and macd_signal is not None and current_macd > macd_signal:
                log("Buying signal")
                allocation_dict["AAPL"] = 1  # Full allocation to AAPL
                
            # Sell Logic: EMA9 below EMA21, RSI below 45, and MACD below signal line
            elif current_ema9 < current_ema21 and current_rsi < 45 and current_macd is not None and macd_signal is not None and current_macd < macd_signal:
                log("Selling signal - Liquidate position")
                allocation_dict["AAPL"] = 0  # No allocation to AAPL

        return TargetAllocation(allocation_dict)