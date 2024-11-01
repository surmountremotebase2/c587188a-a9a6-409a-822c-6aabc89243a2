from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META"]

    @property
    def interval(self):
        return "1hour"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        total_investment = 1000

        for ticker in self.tickers:
            ticker_data = data[ticker]['ohlcv']
            
            # Calculate technical indicators
            ema9 = EMA(ticker, ticker_data, period=9)
            ema21 = EMA(ticker, ticker_data, period=21)
            rsi = RSI(ticker, ticker_data, period=4)
            macd_line, signal_line = MACD(ticker, ticker_data)

            # Check conditions for buying
            if ema9[-1] > ema21[-1] and rsi[-1] > 65 and macd_line[-1] > signal_line[-1]:
                log(f"Investing in {ticker}")
                allocation_dict[ticker] = total_investment / len(self.tickers)  # Distribute investment

            # Check conditions for liquidating
            elif ema9[-1] < ema21[-1] and rsi[-1] < 45 and macd_line[-1] < signal_line[-1]:
                log(f"Liquidating position in {ticker}")
                allocation_dict[ticker] = 0  # Liquidate position

        return TargetAllocation(allocation_dict)