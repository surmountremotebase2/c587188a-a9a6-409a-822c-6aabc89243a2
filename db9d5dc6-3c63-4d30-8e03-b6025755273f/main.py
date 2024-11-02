from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, BB
from .macd import MACD  # Import the MACD function from the macd module

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "WMT", "JPM", "NVDA", "AMD", "META", "TSLA"
        "AMZN", "GOOGL","LMT","NOC", "GC", "BAC", "GS", "PFE", "JNJ","FDX","UNP"]  # Adjusted tickers as needed
        self.total_investment = 3000  # Total investment amount is $3,000
        self.investment_rate = 0.5  # Rate at which to invest (50%)
        self.initial_allocation = self.total_investment * self.investment_rate / len(self.tickers)  # Equal allocation per ticker

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocations to zero
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            close_prices = [day[ticker]['close'] for day in ohlcv if ticker in day]
            rsi_data = RSI(ticker, ohlcv, 14)  # RSI with a period of 14
            ema9 = EMA(ticker, ohlcv, 9)
            ema21 = EMA(ticker, ohlcv, 21)
            bb_data = BB(ticker, ohlcv, 20)

            if len(close_prices) < 1 or len(rsi_data) < 1 or len(ema9) < 1 or len(ema21) < 1 or len(bb_data['upper']) < 1:
                continue

            current_rsi = rsi_data[-1]
            current_ema9 = ema9[-1]
            current_ema21 = ema21[-1]
            current_close = close_prices[-1]
            current_bb_lower = bb_data['lower'][-1]
            current_bb_upper = bb_data['upper'][-1]

            macd_line, signal_line = MACD(close_prices)
            current_macd = macd_line[-1]
            current_signal = signal_line[-1]

            # Investment Conditions
            if (current_close <= current_bb_lower or
                current_ema9 > current_ema21 or
                (current_ema9 > current_ema21 and current_rsi > 51) or
                (current_rsi < 30) or
                (current_macd > current_signal and current_rsi > 50)):
                allocation_dict[ticker] += self.initial_allocation  # Invest 30% of initial investment

            # Liquidation Conditions
            if (current_signal > current_macd and current_rsi < 49) or \
               (current_ema21 > current_ema9 and current_rsi < 50) or \
               (current_close >= current_bb_upper):
                allocation_dict[ticker] = 0  # Liquidate the stock

        # Return the target allocation
        return TargetAllocation(allocation_dict)