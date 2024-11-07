from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, MACD, ADX, ATR, CCI, BB
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]
        # Define additional attributes if needed
        self.investment = 2000  # Total investment shared across all stocks

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        # Choose an appropriate interval based on the strategy
        return "1day"

    def run(self, data):
        allocations = {}

        for ticker in self.tickers:
            # Extracting required technical indicators per stock
            ema21 = EMA(ticker, data, 21)
            ema9 = EMA(ticker, data, 9)
            rsi = RSI(ticker, data, 14)
            adx = ADX(ticker, data, 14)
            atr = ATR(ticker, data, 14)
            cci = CCI(ticker, data, 14)
            macd = MACD(ticker, data, 12, 26)
            bb = BB(ticker, data, 20, 2)

            current_price = data[-1][ticker]['close']

            # View all indicators (Ensure they're not None as checks)
            if None in [ema21, ema9, rsi, adx, atr, cci, macd, bb]:
                allocations[ticker] = 0
                continue

            # Check the buy conditions based on provided logic
            if (macd["MACD"][-1] > macd["signal"][-1]) and (ema21[-1] > ema9[-1]) and (rsi[-1] > 65) and (adx[-1] > 60) and (cci[-1] > 100) and (atr[-1] > 0.6) and (current_price < bb['lower'][-1]) and (rsi[-1] < 30) and (adx[-1] > 60) and (cci[-1] < -100):
                allocations[ticker] = self.allocate_funds()
            
            # Check the sell conditions based on provided logic
            elif (macd["signal"][-1] > macd["MACD"][-1]) and (ema9[-1] > ema21[-1]) and (rsi[-1] < 35) and (cci[-1] < -100) and (atr[-1] > 0.6) and (adx[-1] > 60) and (current_price > bb['upper'][-1]) and (rsi[-1] > 70) and ((atr[-1] > 0.7 and adx[-1] > 70) or (atr[-1] > 0.75 or adx[-1] > 75)) and (cci[-1] > 100):
                allocations[ticker] = 0  # Liquidate stocks meeting sell conditions

        return TargetAllocation(allocations)

    def allocate_funds(self):
        # This method is a placeholder for logic you might want to use to determine 
        # how much of the $2000 to invest in each stock.
        # For simplicity, equally divide the investment by the number of stocks.
        return self.investment / len(self.tickers) / self.investment  # Normalize per stock allocation to 0-1 range