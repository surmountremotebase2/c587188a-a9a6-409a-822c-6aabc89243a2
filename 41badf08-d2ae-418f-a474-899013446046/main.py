from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, MACD, ADX, ATR, CCI, BB, RSI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"  # The interval for market data

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            allocation_dict[ticker] = 0  # Default to no position

            # Calculate indicators
            ema9 = EMA(ticker, data, 9)
            ema21 = EMA(ticker, data, 21)
            macd = MACD(ticker, data, fast=12, slow=26)
            rsi = RSI(ticker, data, 14)
            adx = ADX(ticker, data, 14)
            atr = ATR(ticker, data, 14)
            cci = CCI(ticker, data, 14)
            bb = BB(ticker, data, 20, 2)

            if len(ema9) > 0 and len(ema21) > 0 and len(macd["MACD"]) > 0 and len(macd["signal"]) > 0 and len(rsi) > 0 and \
                  len(adx) > 0 and len(atr) > 0 and len(cci) > 0 and len(bb["lower"]) > 0 and len(data[-1][ticker]['close']) > 0:

                # Implement buy condition checks
                if macd["MACD"][-1] > macd["signal"][-1] and ema21[-1] > ema9[-1] and \
                   rsi[-1] > 65 and adx[-1] > 60 and cci[-1] > 100 and atr[-1] > 0.6 and \
                   data[-1][ticker]['close'] < bb["lower"][-1] and rsi[-1] < 70 and adx[-1] > 65 and cci[-1] < -100:
                    allocation_dict[ticker] = 0.1  # Assign 10% of portfolio to this asset if buy conditions are met

                # Implement sell condition checks
                elif macd["signal"][-1] > macd["MACD"][-1] and ema9[-1] > ema21[-1] and \
                     rsi[-1] < 35 and cci[-1] < -100 and atr[-1] > 0.6 and adx[-1] > 60 and \
                     data[-1][ticker]['close'] > bb["upper"][-1] and rsi[-1] > 70 and \
                     ((atr[-1] > 0.70 and adx[-1] > 70) or (atr[-1] > 0.75 or adx[-1] > 75)) and cci[-1] > 100:
                    allocation_dict[ticker] = -0.1  # Assign -10% of portfolio to this asset if sell conditions are met
            else:
                log(f"Insufficient data for {ticker}")

        return TargetAllocation(allocation_dict)