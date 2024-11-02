from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.technical_indicators import RSI, EMA, BB
from .macd import MACD  # Import the MACD function from the macd module

class TradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        self.total_investment = 3000
        self.data_list = []  # Placeholder for data classes

    @property
    def interval(self):
        return "1hour"  # Changed to 1 hour

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {ticker: self.total_investment / len(self.tickers) for ticker in self.tickers}

        for ticker in self.tickers:
            ohlcv = data["ohlcv"]
            close_prices = [day[ticker]['close'] for day in ohlcv]  # Extract closing prices
            macd_line, signal_line = MACD(close_prices)  # MACD Calculation using custom function
            rsi_data = RSI(ticker, ohlcv, length=4)  # RSI Calculation
            ema_short = EMA(ticker, ohlcv, length=9)  # 9-day EMA
            ema_long = EMA(ticker, ohlcv, length=21)  # 21-day EMA
            bb_data = BB(ticker, ohlcv, length=20)  # Bollinger Bands Calculation

            # MACD Signals
            if len(macd_line) > 1:
                if macd_line[-2] <= signal_line[-2] and macd_line[-1] > signal_line[-1]:
                    log(f"{ticker}: Buy Signal (MACD)")

                if macd_line[-2] > signal_line[-2] and macd_line[-1] <= signal_line[-1]:
                    log(f"{ticker}: Sell Signal (MACD)")

            # RSI Signals
            if rsi_data and len(rsi_data) > 1:
                current_rsi = rsi_data[-1]['rsi']  # Adjust based on expected structure
                rsi_prev = rsi_data[-2]['rsi']
                if current_rsi < 35 and rsi_prev < current_rsi:
                    log(f"{ticker}: Buy Signal (RSI)")

                if current_rsi > 65 and rsi_prev > current_rsi:
                    log(f"{ticker}: Sell Signal (RSI)")

            # EMA Signals
            if ema_short and ema_long and len(ema_short) > 1 and len(ema_long) > 1:
                if ema_short[-1] > ema_long[-1] and ema_short[-2] <= ema_long[-2]:
                    log(f"{ticker}: Buy Signal (EMA)")

                if ema_short[-1] < ema_long[-1] and ema_short[-2] >= ema_long[-2]:
                    log(f"{ticker}: Sell Signal (EMA)")

            # Bollinger Bands Signals
            if bb_data and len(bb_data) > 0:
                current_price = ohlcv[-1][ticker]['close']
                lower_band = bb_data['lower'][-1]  # Accessing the lower band
                upper_band = bb_data['upper'][-1]  # Accessing the upper band
                if current_price <= lower_band:
                    log(f"{ticker}: Buy Signal (Bollinger Bands)")

                if current_price >= upper_band:
                    log(f"{ticker}: Sell Signal (Bollinger Bands)")

        return TargetAllocation(allocation_dict)