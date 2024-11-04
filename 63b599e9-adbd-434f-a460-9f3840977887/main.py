from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import ADX
from .macd import MACD  # Import the MACD function from the macd module

class TradingStrategy(Strategy):  # Changed back to TradingStrategy
    def __init__(self):
        self.tickers = [
            "AAPL", "GOOGL", "AMZN"
            ]  # Add your desired tickers here
        self.previous_signals = {ticker: None for ticker in self.tickers}  # Store previous signal states

    @property
    def interval(self):
        return "1hour"  # Set the interval to 1 hour

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocations to zero
        holding_dict = {ticker: 0 for ticker in self.tickers}  # Track holding amounts
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            close_prices = [day[ticker]['close'] for day in ohlcv if ticker in day]
            adx_data = ADX(ticker, ohlcv, 14)

            macd_line, signal_line = MACD(close_prices)
            if len(close_prices) < 1 or len(adx_data) < 1 or len(macd_line) < 1 or len(signal_line) < 1:
                continue

            # Set current values
            current_macd = macd_line[-1]
            current_signal = signal_line[-1]
            current_adx = adx_data[-1]
            difference = abs(current_macd - current_signal)

            # Entry Condition: MACD line crosses above the signal line
            if current_macd > current_signal and difference > 0.5 and current_adx > 19:
                allocation_dict[ticker] = 2000 / len(self.tickers)  # Invest equally across tickers
                holding_dict[ticker] += allocation_dict[ticker] / close_prices[-1]  # Update holding amount
                self.previous_signals[ticker] = "bullish"

            # Exit Condition: Signal line crosses above the MACD line
            elif current_signal > current_macd and difference > 0.5 and current_adx > 19 and holding_dict[ticker] > 0:
                allocation_dict[ticker] = 0  # Liquidate the stock
                holding_dict[ticker] = 0  # Reset holding amount
                self.previous_signals[ticker] = "bearish"

        # Return the target allocation
        return TargetAllocation(allocation_dict)