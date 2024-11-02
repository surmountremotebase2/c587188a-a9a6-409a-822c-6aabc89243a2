#Type code her# Assuming this is your main.py file
from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.technical_indicators import EMA, MACD, RSI, ATR

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]
        self.initial_investment = 3000

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            try:
                ema_9 = EMA(ticker, ohlcv, 9)[-1]
                ema_21 = EMA(ticker, ohlcv, 21)[-1]

                macd = MACD(ticker, ohlcv, fast=12, slow=26)
                macd_line = macd['macd'][-1] if 'macd' in macd else None
                signal_line = macd['signal'][-1] if 'signal' in macd else None
                
                rsi = RSI(ticker, ohlcv, length=14)[-1]
                atr = ATR(ticker, ohlcv, length=14)[-1]

                if macd_line is not None and signal_line is not None:
                    buy_conditions = [
                        ema_9 > ema_21,
                        macd_line > signal_line,
                        rsi < 30
                    ]

                    if sum(buy_conditions) >= 3:
                        allocation_dict[ticker] = self.initial_investment / len(self.tickers)

                    sell_conditions = [
                        ema_9 < ema_21,
                        macd_line < signal_line,
                        rsi > 70,
                        atr > 0
                    ]

                    if sum(sell_conditions) >= 4:
                        allocation_dict[ticker] = 0

            except Exception as e:
                log(f"Error processing {ticker}: {str(e)}")

        return TargetAllocation(allocation_dict)