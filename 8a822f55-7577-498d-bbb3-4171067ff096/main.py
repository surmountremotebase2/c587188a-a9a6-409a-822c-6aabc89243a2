from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, RSI, BB, ATR, Momentum, Slope  # Ensure all necessary imports are present
from .macd import MACD  # Ensure MACD function is correctly imported

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "NVDA", "GOOGL", "AMZN"]
        self.holding_dict = {ticker: 0 for ticker in self.tickers}
        self.entry_prices = {ticker: 0 for ticker in self.tickers}  # Track entry prices for ATR-based stop loss

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
                len(macd_line) < 1 or len(signal_line) < 1 or len(bb_data['lower']) < 1 or 
                len(bb_data['upper']) < 1 or len(momentum_values) < 1 or len(slope_values) < 1
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
                (current_short_ma > current_long_ma and current_rsi < 40 and (current_macd > current_signal or current_slope_value > 0)) or
                (current_rsi < 35 and current_close <= current_bb_lower and current_momentum_value > 0)
            ):
                allocation_dict[ticker] = 2000 / len(self.tickers)  # Invest equal proportion per ticker
                self.holding_dict[ticker] = allocation_dict[ticker] / current_close  # Update holding amount
                self.entry_prices[ticker] = current_close  # Set the entry price

            # Exit conditions
            elif (
                (current_long_ma > current_short_ma and current_rsi > 60 and current_signal > current_macd and current_slope_value < 0) or
                (current_rsi > 65 and current_close >= current_bb_upper and current_momentum_value < 0)
            ):
                if self.holding_dict[ticker] > 0:
                    allocation_dict[ticker] = 0  # Liquidate the stock
                    self.holding_dict[ticker] = 0  # Reset holding amount

            # Stop-loss based on ATR
            if self.holding_dict[ticker] > 0:
                stop_loss_price = self.entry_prices[ticker] - (1.0 * current_atr)
                if current_close < stop_loss_price:
                    allocation_dict[ticker] = 0  # Liquidate the stock
                    self.holding_dict[ticker] = 0  # Reset holding amount

        # Return the target allocation
        return TargetAllocation(allocation_dict)