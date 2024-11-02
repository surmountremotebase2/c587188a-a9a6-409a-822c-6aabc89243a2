from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, BB
from .macd import MACD  # Import the MACD function from the macd module


class TradingStrategy:
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]
        self.total_investment = 2000
        self.investment_per_stock = self.total_investment / len(self.tickers)
        self.positions = {ticker: 0 for ticker in self.tickers}

    def evaluate_conditions(self, data):
        for ticker in self.tickers:
            # Extract data for indicators
            close_prices = data[ticker]['close']
            ema9 = technical_indicators.EMA(ticker, data, 9)
            ema21 = technical_indicators.EMA(ticker, data, 21)
            macd_line, signal_line = MACD(close_prices)
            rsi = technical_indicators.RSI(ticker, data, 14)
            bollinger_bands = technical_indicators.BB(ticker, data, 20, 2)
            lower_band = bollinger_bands['lower']
            upper_band = bollinger_bands['upper']
            
            # Check Buy Conditions
            buy_condition_1 = (macd_line[-1] > signal_line[-1] and ema9[-1] > ema21[-1] and rsi[-1] < 49)
            buy_condition_2 = (close_prices[-1] <= lower_band[-1])
            buy_condition_3 = (rsi[-1] < 30)

            if buy_condition_1 or buy_condition_2 or buy_condition_3:
                self.buy_stock(ticker)

            # Check Sell Conditions
            sell_condition_1 = (signal_line[-1] > macd_line[-1] and ema21[-1] > ema9[-1] and rsi[-1] > 52)
            sell_condition_2 = (close_prices[-1] >= upper_band[-1])
            sell_condition_3 = (rsi[-1] >= 70)

            if sell_condition_1 or sell_condition_2 or sell_condition_3:
                self.sell_stock(ticker)

    def buy_stock(self, ticker):
        if self.positions[ticker] == 0:  # Only buy if not already holding the stock
            self.positions[ticker] = self.investment_per_stock
            print(f"Bought {ticker} with ${self.investment_per_stock}")

    def sell_stock(self, ticker):
        if self.positions[ticker] > 0:  # Only sell if holding the stock
            print(f"Sold {ticker} with ${self.positions[ticker]}")
            self.positions[ticker] = 0