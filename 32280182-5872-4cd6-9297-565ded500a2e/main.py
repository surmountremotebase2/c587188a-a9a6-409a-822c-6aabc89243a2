from datetime import datetime, timedelta
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, RSI, BB, ATR, Momentum, Slope
from .macd import MACD

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "NVDA", "GOOGL", "AMZN"]
        self.holding_dict = {ticker: 0 for ticker in self.tickers}
        self.entry_prices = {ticker: 0 for ticker in self.tickers}  # Track entry prices for ATR-based stop loss
        self.sell_condition_times = {ticker: None for ticker in self.tickers}  # Track initial sell condition times

    @property
    def interval(self):
        return "1hour"  # Using 1-hour interval

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocations to zero
        ohlcv = data.get("ohlcv")
        current_time = datetime.now()

        for ticker in self.tickers:
            close_prices = [day[ticker]['close'] for day in ohlcv if ticker in day]
            if len(close_prices) < 20:
                continue

            # Indicators
            short_term_ma = SMA(ticker, ohlcv, 5)
            long_term_ma = SMA(ticker, ohlcv, 20)
            rsi = RSI(ticker, ohlcv, 9)
            macd_line, signal_line = MACD(close_prices, 9, 21, 8)
            bb_data = BB(ticker, ohlcv, 10, 2)
            atr = ATR(ticker, ohlcv, 10)
            momentum_values = Momentum(ticker, ohlcv, length=10)
            slope_values = Slope(ticker, ohlcv, length=5)

            if len(short_term_ma) < 1 or len(long_term_ma) < 1 or len(rsi) < 1 or len(macd_line) < 1 or len(signal_line) < 1:
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

            # Buy conditions
            buy_conditions_met = sum([
                current_rsi < 30 and current_macd > current_signal,  # RSI below 30 and MACD crosses above signal line
                current_close <= current_bb_lower and current_rsi < 30,  # Price below lower Bollinger Band and RSI < 30
                current_slope_value > 0 and current_momentum_value > 0,  # Positive slope and increasing momentum
                current_macd > current_signal and current_rsi > 55,  # MACD crosses above signal line and RSI > 55
            ])

            if buy_conditions_met >= 1:  # Buy if 3 out of 4 conditions are met
                allocation_dict[ticker] += 0.3 * (2000 / len(self.tickers))  # Allocate 30% per condition met
                self.holding_dict[ticker] += allocation_dict[ticker] / current_close
                self.entry_prices[ticker] = current_close

            # Sell conditions
            sell_conditions_met = sum([
                current_rsi > 70 and current_macd < current_signal,  # RSI above 70 and MACD crosses below signal line
                current_close >= current_bb_upper and current_rsi > 70,  # Price above upper Bollinger Band and RSI > 70
                current_slope_value < 0 and current_momentum_value < 0,  # Negative slope and weakening momentum
                current_macd < current_signal and current_rsi < 45,  # MACD crosses below signal line and RSI < 45
            ])

            if sell_conditions_met >= 1:
                if self.sell_condition_times[ticker] is None:
                    # Record the current time if this is the first occurrence
                    self.sell_condition_times[ticker] = current_time
                elif current_time >= self.sell_condition_times[ticker] + timedelta(minutes=5):
                    # Check if 5 minutes have passed since the initial occurrence
                    allocation_dict[ticker] = 0  # Liquidate the stock
                    self.holding_dict[ticker] = 0
                    self.sell_condition_times[ticker] = None  # Reset the timer
            else:
                self.sell_condition_times[ticker] = None  # Reset if conditions are no longer met

            # Stop-loss based on ATR
            if self.holding_dict[ticker] > 0:
                stop_loss_price = self.entry_prices[ticker] - (1.0 * current_atr)
                if current_close < stop_loss_price:
                    allocation_dict[ticker] = 0  # Liquidate the stock
                    self.holding_dict[ticker] = 0

        # Return the target allocation
        return TargetAllocation(allocation_dict)