from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, BB, ADX
from .macd import MACD  # Import the MACD function from the macd module

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = [
            "AAPL"#, "GOOGL"#, "META", "AMZN"
            #"NVDA", "AMD", "TSLA", "WMT" #, "PLTR"
        ]  # Adjusted tickers as needed

    @property
    def interval(self):
        return "5min"  # Using 5-minute interval

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocations to zero
        holding_dict = {ticker: 0 for ticker in self.tickers}  # Track holding amounts
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            # Extract necessary data
            close_prices = [day[ticker]['close'] for day in ohlcv if ticker in day]
            rsi_data = RSI(ticker, ohlcv, 14)
            ema9 = EMA(ticker, ohlcv, 9)
            ema21 = EMA(ticker, ohlcv, 21)
            bb_data = BB(ticker, ohlcv, 20, 2)
            adx_data = ADX(ticker, ohlcv, 14)

            # Ensure enough data points are available
            if len(close_prices) < 3 or len(rsi_data) < 3 or len(ema9) < 3 or len(ema21) < 3 or len(bb_data['upper']) < 3:
                continue

            # Current values
            current_close = close_prices[-1]
            current_rsi = rsi_data[-1]
            current_adx = adx_data[-1]
            current_ema9 = ema9[-1]
            current_ema21 = ema21[-1]
            macd_line, signal_line = MACD(close_prices)
            current_macd = macd_line[-1]
            current_signal = signal_line[-1]

            # Waiting period: Ensure signals are persistent over the last three intervals
            rsi_signal_persistent = all(rsi < 30 or rsi > 50 for rsi in rsi_data[-3:])
            adx_signal_persistent = all(adx > 20 for adx in adx_data[-3:])
            ema_signal_persistent = all(ema9 > ema21 for ema9, ema21 in zip(ema9[-3:], ema21[-3:]))

            # Investment Conditions: Only proceed if all signals are persistent
            if rsi_signal_persistent and adx_signal_persistent and ema_signal_persistent:
                allocation_dict[ticker] = 2000 / len(self.tickers)  # Invest equal proportion per ticker
                holding_dict[ticker] += allocation_dict[ticker] / current_close  # Update holding amount

            # Stop-loss condition: Liquidate if the price drops 3% within 1 hour, 4 hours, or 1 day
            # (This part requires your data structure to support time-based checks, not shown in this snippet)

            # Liquidation Conditions
            current_value = holding_dict[ticker] * current_close
            liquidate_value = allocation_dict[ticker] * 1.03  # Adjusted for quicker profit-taking

            if current_adx > 20 and current_rsi < 50:
                if (
                    (current_signal > current_macd and current_rsi < 45) or  # Conservative RSI threshold
                    (current_ema21 > current_ema9 and current_rsi < 45) or
                    current_rsi > 70 or
                    current_close >= bb_data['upper'][-1]
                ):
                    if current_value > liquidate_value:  # Only liquidate if current value is greater than the allocation
                        allocation_dict[ticker] = 0  # Liquidate the stock
                        holding_dict[ticker] = 0  # Reset holding amount

        # Return the target allocation
        return TargetAllocation(allocation_dict)