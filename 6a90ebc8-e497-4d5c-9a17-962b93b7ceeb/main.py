from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, SMA, RSI, MACD, BB, SO, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "NVDA", "GOOGL", "AMZN"]
        # Data list is not necessary to define in the init as indicators are directly accessed

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            # Moving Averages
            ma_short = SMA(ticker, data["ohlcv"], 5)
            ma_long = SMA(ticker, data["ohlcv"], 20)
            # RSI
            rsi = RSI(ticker, data["ohlcv"], 9)
            # MACD
            macd = MACD(ticker, data["ohlcv"], fast=9, slow=21, signal_period=8)
            # Bollinger Bands
            bb = BB(ticker, data["ohlcv"], length=10, std=2)
            # Stochastic Oscillator
            stoch = SO(ticker, data["ohlcv"], k=13, d=3)
            # ATR for Stop Loss (Though mechanism of implementing stop loss is not detailed here)
            atr = ATR(ticker, data["ohlcv"], 10)
            
            # Assuming last close data for the comparison
            close_price = data["ohlcv"][-1][ticker]['close']
            
            # Buy Conditions
            if ma_short[-1] > ma_long[-1] and rsi[-1] > 60 and macd["MACD"][-1] > macd["signal"][-1] \
               and close_price <= bb["lower"][-1] and stoch["k"][-1] < 18:
                allocation_dict[ticker] = 0.25  # equally distribute investment among 4 stocks

            # Sell Conditions
            elif ma_long[-1] > ma_short[-1] or rsi[-1] > 65 or macd["MACD"][-1] < macd["signal"][-1] \
                 or close_price >= bb["upper"][-1] or stoch["k"][-1] > 80:
                allocation_dict[ticker] = 0  # Sell the stock

            else:
                allocation_dict[ticker] = 0  # Neutral, hold or do nothing with the position

        return TargetAllocation(allocation_dict)