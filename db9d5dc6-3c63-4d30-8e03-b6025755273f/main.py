from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, BB
from .macd import MACD  # Import the MACD function from the macd module

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]
        self.data_list = []
        self.total_investment = 3000  # Total investment amount

    @property
    def interval(self):
        return "1hour"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {ticker: self.total_investment / len(self.tickers) for ticker in self.tickers}
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            close_prices = [day[ticker]['close'] for day in ohlcv if ticker in day]
            rsi_data = RSI(ticker, ohlcv, 4)
            ema9 = EMA(ticker, ohlcv, 9)
            ema21 = EMA(ticker, ohlcv, 21)
            bb_data = BB(ticker, ohlcv, 20)

            if len(close_prices) < 1 or len(rsi_data) < 1 or len(ema9) < 1 or len(ema21) < 1 or len(bb_data['lower']) < 1:
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

            # Entry Conditions to Buy
            if (current_ema9 > current_ema21 and
                current_rsi > 65 and
                current_macd > current_signal and
                current_close >= current_bb_lower):  # Adjust this line to check upward movement
                allocation_dict[ticker] += allocation_dict[ticker] * 0.1  # Increase allocation for entry

            # Liquidate Conditions
            elif (current_ema9 < current_ema21 and
                  current_rsi < 45 and
                  current_macd < current_signal and
                  current_close <= current_bb_upper):  # Adjust this line to check downward movement
                allocation_dict[ticker] -= allocation_dict[ticker] * 0.1  # Decrease allocation for liquidation

        # Normalize allocations
        total_allocation = sum(allocation_dict.values())
        normalized_allocation = {ticker: allocation / total_allocation for ticker, allocation in allocation_dict.items()}

        return TargetAllocation(normalized_allocation)