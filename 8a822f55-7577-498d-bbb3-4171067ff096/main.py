from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, RSI, BB, ATR, Momentum, Slope  # Removed Stochastic
from .macd import MACD  # Ensure MACD function is correctly imported
import time  # Import time to manage timestamps

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "NVDA", "GOOGL", "AMZN"]
        self.holding_dict = {ticker: 0 for ticker in self.tickers}
        self.entry_prices = {ticker: 0 for ticker in self.tickers}  # Track entry prices for ATR-based stop loss
        self.entry_times = {ticker: None for ticker in self.tickers}  # Track entry times

    @property
    def interval(self):
        return "1hour"  # Set the interval to 1 hour

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocations to zero
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            close_prices = [day[ticker]['close'] for day in ohlcv if ticker in day]
            if len(close_prices) < 20:  # Ensure there are enough data points
                continue

            # Indicators
            short_term_ma = SMA(ticker, ohlcv, 5)  # Short-term moving average
            long_term_ma = SMA(ticker, ohlcv, 20)  # Long-term moving average
            rsi = RSI(ticker, ohlcv, 9)
            macd_line, signal_line = MACD(close_prices, 9, 21, 8)
            bb_data = BB(ticker, ohlcv, 10, 2)
            atr = ATR(ticker, ohlcv, 10)
            momentum_values = Momentum(ticker, ohlcv, length=10)
            slope_values = Slope(ticker, ohlcv, length=5)

            # Ensure there are enough data points for all indicators
            if (
                len(short_term_ma) < 1 or len(long_term_ma) < 1 or len(rsi) < 1 or 
                len(macd_line) < 1 or len(signal_line) < 1 or 
                len(bb_data['lower']) < 1 or len(bb_data['upper']) < 1 or 
                len(momentum_values) < 1 or len(slope_values) < 1
            ):
                continue

            # Current values
            current_short_ma = short_term_ma[-1]
            current_long_ma = long_term_ma[-1]
            current_rsi = rsi[-1]
            current_macd = macd_line[-1]
            current_signal = signal_line[-1]
            current_close = close_prices[-1]
            current_bb_lower = bb_data['lower'][-1]
            current_bb_upper = bb_data['upper'][-1]
            current_atr = atr[-1]
            current_momentum_value = momentum_values[-1]
            current_slope_value = slope_values[-1]

            # Entry conditions
            if (
                (current_short_ma > current_long_ma and  # Short-term MA above long-term MA
                current_rsi < 40 and  # RSI below 40
                current_macd > current_signal and  # MACD line above signal line
                current_close <= current_bb_lower and  # Price touches or goes below lower Bollinger Band
                (current_momentum_value > 0 or current_slope_value > 0))  # Momentum or slope is positive
            ):
                if self.holding_dict[ticker] == 0:  # Check if we are not already holding
                    allocation_dict[ticker] = 2000 / len(self.tickers)  # Invest equal proportion per ticker
                    self.holding_dict[ticker] = allocation_dict[ticker] / current_close  # Update holding amount
                    self.entry_prices[ticker] = current_close  # Set the entry price
                    self.entry_times[ticker] = time.time()  # Record entry time

            # Check if we have held the position for at least 30 minutes (1800 seconds)
            if self.holding_dict[ticker] > 0 and (time.time() - self.entry_times[ticker]) >= 1800:
                # Exit conditions
                if (
                    (current_long_ma > current_short_ma and  # Long-term MA above short-term MA
                    current_rsi > 60 and  # RSI above 60
                    current_signal > current_macd and  # Signal line above MACD line
                    current_slope_value < 0) or  # Slope is negative
                    current_close >= current_bb_upper or  # Price touches or goes above upper Bollinger Band
                    (current_momentum_value < 0 and current_rsi > 65)  # Momentum is negative and RSI above 65
                ):
                    allocation_dict[ticker] = 0  # Liquidate the stock
                    self.holding_dict[ticker] = 0  # Reset holding amount
                    self.entry_times[ticker] = None  # Reset entry time

            # Stop-loss based on ATR
            if self.holding_dict[ticker] > 0:
                stop_loss_price = self.entry_prices[ticker] - (1.0 * current_atr)
                if current_close < stop_loss_price:
                    allocation_dict[ticker] = 0  # Liquidate the stock
                    self.holding_dict[ticker] = 0  # Reset holding amount
                    self.entry_times[ticker] = None  # Reset entry time

        # Return the target allocation
        return TargetAllocation(allocation_dict)