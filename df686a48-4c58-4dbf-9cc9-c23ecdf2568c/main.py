from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD

class TradingStrategy(Strategy):
    @property
    def interval(self):
        return "1hour"  # Set to 1-hour intervals in a supported format

    @property
    def assets(self):
        return ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META", "AVGO"]

    def run(self, data):
        allocations = {}
        num_assets = len(self.assets)  # Count the number of assets
        investment_per_stock = 1000  # Define an investment amount
        capital = sum(allocations.get(ticker, 0) for ticker in self.assets)  # Current capital

        for ticker in self.assets:
            ohlcv = data.get("ohlcv")[ticker]

            # Calculate EMA9, EMA21, RSI(4), and MACD
            ema9 = EMA(ticker, ohlcv, 9)
            ema21 = EMA(ticker, ohlcv, 21)
            rsi = RSI(ticker, ohlcv, 4)
            macd_data = MACD(ticker, ohlcv, fast=12, slow=26)
            macd_line = macd_data["macd"]
            signal_line = macd_data["signal"]

            # Entry condition: Buy when EMA9 > EMA21, RSI > 65, MACD > Signal
            if ema9[-1] > ema21[-1] and rsi[-1] > 65 and macd_line[-1] > signal_line[-1]:
                allocations[ticker] = investment_per_stock / capital  # Allocate equal percentage

            # Exit condition: Sell when EMA9 < EMA21, RSI < 45, MACD < Signal
            elif ema9[-1] < ema21[-1] and rsi[-1] < 45 and macd_line[-1] < signal_line[-1]:
                allocations[ticker] = 0  # Liquidate the position

        return TargetAllocation(allocations)