from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "TSLA", "MSFT", "NVDA", "AMD"]

    @property
    def interval(self):
        return "1hour"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            ema9 = EMA(ticker, data["ohlcv"], length=9)
            ema21 = EMA(ticker, data["ohlcv"], length=21)
            rsi = RSI(ticker, data["ohlcv"], length=4)
            # The strategy checks for the last values of EMA9, EMA21, and RSI(4)
            if ema9[-1] > ema21[-1] and rsi[-1] > 65:
                # Assuming equal distribution of $1000 among assets which meet conditions
                allocation_dict[ticker] = 1 / len(self.tickers)
            elif ema9[-1] < ema21[-1] and rsi[-1] < 45:
                # Liquidate the position for this asset
                allocation_dict[ticker] = 0
            else:
                # No action for this asset, so no allocation
                continue

        # If no stock meets the condition, then allocation_dict could be empty. In such case, this means hold cash
        if not allocation_dict:
            for ticker in self.tickers:
                allocation_dict[ticker] = 0
                
        return TargetAllocation(allocation_dict)