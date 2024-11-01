#Type code here
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI

class MomentumEMAStrategy(Strategy):
    @property
    def interval(self):
        return "1h"  # Set to 1-hour intervals

    @property
    def assets(self):
        return ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META", "AVGO"]

    def run(self, data):
        allocations = {}
        num_assets = len(self.assets)  # Count the number of assets
        equal_percentage = 1 / num_assets  # Calculate equal percentage for each asset

        for ticker in self.assets:
            ohlcv = data.get("ohlcv")[ticker]

            # Calculate EMAs
            ema9 = EMA(ticker, ohlcv, 9)
            ema21 = EMA(ticker, ohlcv, 21)
            ema12 = EMA(ticker, ohlcv, 12)
            ema26 = EMA(ticker, ohlcv, 26)
            ema_diff = ema12[-1] - ema26[-1]  # Difference between EMA12 and EMA26
            ema_diff_9 = EMA(ticker, [ema12[i] - ema26[i] for i in range(len(ema12))], 9)

            # Calculate RSI
            rsi = RSI(ticker, ohlcv, 14)

            # Entry Condition: Buy when EMA9 > EMA21, RSI > 65, and EMA12 - EMA26 > 9-day EMA of EMA diff
            if ema9[-1] > ema21[-1] and rsi[-1] > 65 and ema_diff > ema_diff_9[-1]:
                allocations[ticker] = equal_percentage  # Allocate an equal percentage to this stock

            # Exit Condition: Sell when EMA9 < EMA21, RSI < 45, and EMA12 - EMA26 < 9-day EMA of EMA diff
            elif ema9[-1] < ema21[-1] and rsi[-1] < 45 and ema_diff < ema_diff_9[-1]:
                allocations[ticker] = 0  # Liquidate the position

        return TargetAllocation(allocations)