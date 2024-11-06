from datetime import datetime, timedelta
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, RSI, BB, ATR, Momentum, Slope, ADX, EMA
from .macd import MACD

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["META","AAPL", "AMZN", "NFLX", "GOOGL", "TSLA", "NVDA", "MSFT", "AMD"]
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
            ema9 = EMA(ticker, ohlcv, 9)
            ema21 = EMA(ticker, ohlcv, 21)
            rsi = RSI(ticker, ohlcv, 9)
            macd_line, signal_line = MACD(close_prices, 9, 21, 8)
            bb_data = BB(ticker, ohlcv, 20, 2)
            momentum_values = Momentum(ticker, ohlcv, length=10) #momentum_values = Momentum(ticker, ohlcv, length=10)
            slope_values = Slope(ticker, ohlcv, length=5)
            adx = ADX(ticker, ohlcv, 10) #adx = ADX(ticker, ohlcv, 14)
            atr = ATR(ticker, ohlcv, 8) #atr = ATR(ticker, ohlcv, 10)

            if len(ema9) < 1 or len(ema21) < 1 or len(rsi) < 1 or len(macd_line) < 1 or len(signal_line) < 1:
                continue

            # Current values
            current_ema9 = ema9[-1]
            current_ema21 = ema21[-1]
            current_rsi = rsi[-1]
            current_macd = macd_line[-1]
            current_signal = signal_line[-1]
            current_close = close_prices[-1]
            current_bb_lower = bb_data['lower'][-1]
            current_bb_upper = bb_data['upper'][-1]
            current_momentum_value = momentum_values[-1]
            current_slope_value = slope_values[-1]
            current_adx = adx[-1]
            current_atr = atr[-1]

            # Buy conditions (if 3 out of 4 conditions are met)
            buy_conditions_met = sum([
                current_slope_value > 0,  # Slope is positive
                current_momentum_value > 0,  # Momentum is positive
                current_ema9 > current_ema21 and current_rsi < 65 and current_adx > 20,  # EMA9 crosses above EMA21 and RSI > 55
                current_close <= current_bb_lower and current_adx > 20 and current_momentum_value > 5,
            ])

            if buy_conditions_met >= 3:
                allocation_dict[ticker] += (buy_conditions_met / 4) * (3000 / len(self.tickers))
                self.holding_dict[ticker] += allocation_dict[ticker] / current_close
                self.entry_prices[ticker] = current_close

            # Sell conditions (if 3 out of 4 conditions are met)
            sell_conditions_met = sum([
                current_slope_value < 0,  # Slope is negative
                current_momentum_value < 0,  # Momentum is negative
                current_ema21 > current_ema9 and current_rsi < 35 and current_adx > 20,  # EMA21 crosses above EMA9 and RSI < 45
                current_close >= current_bb_upper and current_adx > 20 and current_momentum_value < 0,
            ])

            if sell_conditions_met >= 3:
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
                stop_loss_price = self.entry_prices[ticker] - (1.05 * current_atr)  # ATR-based stop loss with adjusted multiplier
                if current_close < stop_loss_price:
                    allocation_dict[ticker] = 0  # Liquidate the stock
                    self.holding_dict[ticker] = 0

        # Return the target allocation
        return TargetAllocation(allocation_dict)