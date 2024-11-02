import pandas as pd
from .macd import MACD  # Import the MACD function from macd.py
from surmount import technical_indicators  # Ensure to import the correct indicators
from surmount.base_class import Strategy  # Import the Strategy base class


class TradingStrategy(Strategy):
    def __init__(self):
        super().__init__()  # Call the constructor of the base class
        self.tickers = ["AAPL"]  # Uncomment other tickers when needed
        self.total_investment = 2000  # Updated total investment amount
        self.allocation = self.total_investment / len(self.tickers)  # Equal allocation
        self.positions = {ticker: 0 for ticker in self.tickers}

    @property
    def assets(self):
        """Return the assets to trade."""
        return self.tickers

    @property
    def interval(self):
        """Return the trading interval (e.g., '1h', '1d')."""
        return '1hour'  # Change to your desired interval

    def get_ohlcv_data(self, ticker):
        # Placeholder for data retrieval function, replace with actual method
        pass

    def generate_signals(self, ticker, data):
        close_prices = [item['close'] for item in data]
        
        # Calculate technical indicators
        macd_line, signal_line = MACD(close_prices)
        ema9 = technical_indicators.EMA(ticker, data, length=9)
        ema21 = technical_indicators.EMA(ticker, data, length=21)
        rsi = technical_indicators.RSI(ticker, data, length=14)  # RSI set to 14
        bollinger_bands = technical_indicators.BB(ticker, data, length=20, std=2)
        
        # Extract current values
        current_macd = macd_line[-1]
        current_signal = signal_line[-1]
        current_ema9 = ema9[-1]
        current_ema21 = ema21[-1]
        current_rsi = rsi[-1]
        current_price = close_prices[-1]
        lower_band = bollinger_bands['lower'][-1]
        upper_band = bollinger_bands['upper'][-1]

        # Entry conditions
        if (
            (current_macd > current_signal and current_ema9 > current_ema21 and current_rsi < 40) or
            (current_price <= lower_band) or
            (current_rsi < 30)
        ):
            return 'buy'

        # Exit conditions
        if (
            (current_signal > current_macd and current_ema21 > current_ema9 and current_rsi > 60) or
            (current_price >= upper_band) or
            (current_rsi >= 70)
        ):
            return 'sell'

        return 'hold'

    def run(self, start_date, end_date):
        for ticker in self.tickers:
            data = self.get_ohlcv_data(ticker)  # Fetch data for each ticker
            signal = self.generate_signals(ticker, data)

            if signal == 'buy' and self.positions[ticker] == 0:
                self.positions[ticker] = self.allocation / data[-1]['close']
                print(f"Bought {ticker} with {self.allocation} at {data[-1]['close']}")
            elif signal == 'sell' and self.positions[ticker] > 0:
                proceeds = self.positions[ticker] * data[-1]['close']
                print(f"Sold {ticker} for {proceeds} at {data[-1]['close']}")
                self.positions[ticker] = 0