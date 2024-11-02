from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, BB
from .macd import MACD  # Import the MACD function from the macd module

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT"]  # Consider uncommenting other tickers for more diversification
        self.total_investment = 2000  # Total investment amount of $2,000
        self.initial_allocation = self.total_investment / len(self.tickers)  # Initial equal allocation per ticker
        self.max_allocation = self.total_investment  # Maximum total investment

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
            if len(close_prices) < 20:  # Ensure there is enough data for the indicators
                continue

            # Calculate indicators
            rsi_data = RSI(ticker, ohlcv, 14)  # Use 14-period RSI
            ema9 = EMA(ticker, ohlcv, 9)
            ema21 = EMA(ticker, ohlcv, 21)
            bb_data = BB(ticker, ohlcv, 20)

            if not rsi_data or not ema9 or not ema21 or not bb_data['upper']:
                continue  # Skip if any indicator returns insufficient data

            # Get the latest values
            current_rsi = rsi_data[-1]
            current_ema9 = ema9[-1]
            current_ema21 = ema21[-1]
            current_close = close_prices[-1]
            current_bb_upper = bb_data['upper'][-1]
            current_bb_lower = bb_data['lower'][-1]

            # Calculate MACD
            macd_line, signal_line = MACD(close_prices)
            if not macd_line or not signal_line:
                continue  # Skip if MACD calculation fails

            current_macd = macd_line[-1]
            current_signal = signal_line[-1]

            # Entry Conditions to Buy (incremental)
            if (current_close <= current_bb_lower or
                current_macd > current_signal or
                current_ema9 > current_ema21 or
                current_rsi > 65):
                # Incrementally increase allocation
                current_allocation = allocation_dict[ticker]
                additional_allocation = self.initial_allocation * 0.5  # Incremental buy (50% of initial allocation)
                new_allocation = min(current_allocation + additional_allocation, self.max_allocation / len(self.tickers))
                allocation_dict[ticker] = new_allocation

            # Liquidation Conditions to Sell
            elif current_signal > current_macd:
                allocation_dict[ticker] = 0  # Liquidate the stock

        # Return the target allocation
        return TargetAllocation(allocation_dict)