from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, MACD, RSI

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
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
                # Calculate EMAs
                ema_9 = EMA(ticker, ohlcv, 9)[-1]
                ema_21 = EMA(ticker, ohlcv, 21)[-1]
                ema_12 = EMA(ticker, ohlcv, 12)[-1]
                ema_26 = EMA(ticker, ohlcv, 26)[-1]

                # Calculate MACD
                macd = MACD(ticker, ohlcv, fast=12, slow=26)
                macd_line = macd['macd'][-1] if 'macd' in macd else None
                signal_line = macd['signal'][-1] if 'signal' in macd else None
                
                # Calculate RSI
                rsi = RSI(ticker, ohlcv, length=4)[-1]

                # Check buy conditions
                buy_conditions = (
                    macd_line is not None and
                    signal_line is not None and
                    macd_line > signal_line and  # MACD line crosses above the signal line
                    ema_9 > ema_21 and            # EMA9 is above EMA21
                    rsi > 65                       # RSI(4) is greater than 65
                )

                # Check sell conditions
                sell_conditions = (
                    macd_line is not None and
                    signal_line is not None and
                    macd_line < signal_line and  # Signal line crosses above the MACD line
                    ema_9 < ema_21 and            # EMA9 is below EMA21
                    rsi < 45                       # RSI(4) falls below 45
                )

                # Execute buy
                if buy_conditions:
                    allocation_dict[ticker] = self.initial_investment / len(self.tickers)

                # Execute sell
                if sell_conditions:
                    allocation_dict[ticker] = 0

            except Exception:
                # Handle exceptions silently
                pass

        return TargetAllocation(allocation_dict)