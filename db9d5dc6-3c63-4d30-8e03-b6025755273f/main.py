from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, BB, ADX
from .macd import MACD  # Import the MACD function from the macd module

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = [
            "META", "AAPL", "AMZN", "NFLX", "GOOGL", "NVDA", "AMD",
            "MSFT", "TSLA", "PFE"#, "PLTR"
        ]  # Adjusted tickers as needed

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocations to zero
        holding_dict = {ticker: 0 for ticker in self.tickers}  # Track holding amounts
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            close_prices = [day[ticker]['close'] for day in ohlcv if ticker in day]
            rsi_data = RSI(ticker, ohlcv, 14)   # RSI with a period of 14
            ema9 = EMA(ticker, ohlcv, 9)        # EMA with a period of 9
            ema21 = EMA(ticker, ohlcv, 21)      # EMA with a period of 21
            bb_data = BB(ticker, ohlcv, 20, 2)  # Bollinger Bands length 20 std 2
            adx = ADX(ticker, ohlcv, 14)        # Calculate ADX from surmount

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

            # Stop-loss condition: Liquidate if current price drops more than 5% from holding value
            if holding_dict[ticker] > 0 and current_close < (holding_dict[ticker] * 0.95):
                allocation_dict[ticker] = 0  # Liquidate stock due to stop-loss
                holding_dict[ticker] = 0  # Reset holding amount

            # Investment Conditions
            if (current_close <= current_bb_lower or
                current_ema9 > current_ema21 or
                (current_ema9 > current_ema21 and current_rsi > 52) or
                (current_rsi < 35) or
                (current_macd > current_signal and current_rsi > 52)):
                allocation_dict[ticker] = 1.0 / len(self.tickers)  # Invest equal proportion per ticker
                holding_dict[ticker] += allocation_dict[ticker] / current_close  # Update holding amount

            # Liquidation Conditions
            current_value = holding_dict[ticker] * current_close
            liquidate_value = allocation_dict[ticker] * 1.15  # The value to compare against

            if (current_signal > current_macd and current_rsi < 48) or \
               (current_ema21 > current_ema9 and current_rsi < 48) or \
               (current_rsi > 70) or \
               (current_close >= current_bb_upper):
                if current_value > liquidate_value:  # Only liquidate if the current value is greater than the allocation
                    allocation_dict[ticker] = 0  # Liquidate the stock
                    holding_dict[ticker] = 0  # Reset holding amount

        # Return the target allocation
        return TargetAllocation(allocation_dict)