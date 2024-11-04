from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, BB, ADX
from .macd import MACD  # Import the MACD function from the macd module

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = [
            "AAPL", "GOOGL", "AMZN"  # Adjusted tickers as needed
        ]
        self.previous_signals = {ticker: None for ticker in self.tickers}  # Store previous signal states

    @property
    def interval(self):
        return "1hour"  # Set interval to 5 minutes

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocations to zero
        holding_dict = {ticker: 0 for ticker in self.tickers}  # Track holding amounts
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            close_prices = [day[ticker]['close'] for day in ohlcv if ticker in day]
            rsi_data = RSI(ticker, ohlcv, 14)
            ema9 = EMA(ticker, ohlcv, 9)
            ema21 = EMA(ticker, ohlcv, 21)
            bb_data = BB(ticker, ohlcv, 20, 2)
            adx = ADX(ticker, ohlcv, 14)

            if len(close_prices) < 1 or len(rsi_data) < 1 or len(ema9) < 1 or len(ema21) < 1 or len(bb_data['upper']) < 1:
                continue

            # Set current values for RSI, EMA, BB, ADX
            current_rsi = rsi_data[-1]
            current_ema9 = ema9[-1]
            current_ema21 = ema21[-1]
            current_close = close_prices[-1]
            current_bb_lower = bb_data['lower'][-1]
            current_bb_upper = bb_data['upper'][-1]
            current_adx = adx[-1]

            macd_line, signal_line = MACD(close_prices)
            current_macd = macd_line[-1]
            current_signal = signal_line[-1]

            # Calculate the highest prices over specified intervals
            highest_1hour = max(close_prices[-12:]) if len(close_prices) >= 12 else current_close
            highest_4hour = max(close_prices[-48:]) if len(close_prices) >= 48 else current_close
            highest_1day = max(close_prices[-288:]) if len(close_prices) >= 288 else current_close

            # Stop-loss condition: Liquidate if the current price drops 3% within any of the specified periods
            if holding_dict[ticker] > 0 and (
                current_close < highest_1hour * 0.97 or
                current_close < highest_4hour * 0.97 or
                current_close < highest_1day * 0.97
            ):
                allocation_dict[ticker] = 0  # Liquidate stock due to stop-loss
                holding_dict[ticker] = 0  # Reset holding amount
                self.previous_signals[ticker] = None  # Reset previous signal on liquidation

            # Current signal evaluation
            current_signal_valid = (current_rsi < 30 or current_rsi > 50) and current_adx > 20 and (
                current_close <= current_bb_lower or
                current_ema9 > current_ema21 or
                (current_ema9 > current_ema21 and current_rsi > 55) or  # More aggressive bullish confirmation
                (current_macd > current_signal and current_rsi > 55)  # Strengthened MACD condition
            )

            # Delayed entry logic: check the previous signal
            if current_signal_valid and self.previous_signals[ticker] is True:
                allocation_dict[ticker] = 2000 / len(self.tickers)  # Invest equal proportion per ticker
                holding_dict[ticker] += allocation_dict[ticker] / current_close  # Update holding amount
            else:
                self.previous_signals[ticker] = current_signal_valid  # Store the current signal state for the next interval

            # Liquidation Conditions
            current_value = holding_dict[ticker] * current_close
            liquidate_value = allocation_dict[ticker] * 1.05  # Adjusted for quicker profit-taking

            if current_adx > 20 and current_rsi < 50:
                if (current_signal > current_macd and current_rsi < 45 or  # Maintain a conservative RSI threshold
                    current_ema21 > current_ema9 and current_rsi < 45 or
                    current_rsi > 70 or
                    current_close >= current_bb_upper):
                    if current_value > liquidate_value:  # Only liquidate if the current value is greater than the allocation
                        allocation_dict[ticker] = 0  # Liquidate the stock
                        holding_dict[ticker] = 0  # Reset holding amount
                        self.previous_signals[ticker] = None  # Reset previous signal on liquidation
                else:
                    continue

        # Return the target allocation
        return TargetAllocation(allocation_dict)