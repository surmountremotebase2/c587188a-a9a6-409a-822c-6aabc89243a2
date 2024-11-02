from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, BB
from .macd import MACD  # Import the MACD function from the macd module

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT"]#, "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]
        self.total_investment = 2000  # Total investment amount is $2,000
        self.initial_allocation = self.total_investment / len(self.tickers)  # Equal allocation per ticker

    @property
    def interval(self):
        return "1hour"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocations to zero
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            close_prices = [day[ticker]['close'] for day in ohlcv if ticker in day]
            rsi_data = RSI(ticker, ohlcv, 17)  # Updated RSI to use a 17-day period
            ema9 = EMA(ticker, ohlcv, 9)
            ema21 = EMA(ticker, ohlcv, 21)
            bb_data = BB(ticker, ohlcv, 20)

            if len(close_prices) < 1 or len(rsi_data) < 1 or len(ema9) < 1 or len(ema21) < 1 or len(bb_data['upper']) < 1:
                continue

            current_rsi = rsi_data[-1]
            current_ema9 = ema9[-1]
            current_ema21 = ema21[-1]
            current_close = close_prices[-1]
            current_bb_upper = bb_data['upper'][-1]

            macd_line, signal_line = MACD(close_prices)
            current_macd = macd_line[-1]
            current_signal = signal_line[-1]

            # Entry Conditions to Buy
            if ((current_macd > current_signal and current_ema9 > current_ema21 and current_rsi < 40) or  # 1st condition
                (current_close <= bb_data['lower'][-1] and current_signal > current_macd) or  # 2nd condition: Price touches or is below the lower BB
                (current_rsi < 30)):  # 3rd condition: RSI(17) < 30
                allocation_dict[ticker] += self.initial_allocation  # Buy with equal allocation

            # Liquidation Conditions to Sell
            elif ((current_signal > current_macd or current_ema21 > current_ema9 and current_rsi > 55) or  # 1st condition
                  (current_close >= current_bb_upper) or  # 2nd condition: Price touches or is above the upper BB
                  (current_rsi > 70)):  # 3rd condition: RSI(17) >= 70
                allocation_dict[ticker] = 0  # Liquidate the stock

        # Return the target allocation
        return TargetAllocation(allocation_dict)