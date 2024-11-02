from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        self.initial_investment = 3000

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        ohlcv = data.get("ohlcv")

        for ticker in self.tickers:
            try:
                # Calculate MACD values
                macd = MACD(ticker, ohlcv, fast=12, slow=26)

                if 'macd' in macd and 'signal' in macd:
                    macd_line = macd['macd'][-1]  # Most recent MACD value
                    signal_line = macd['signal'][-1]  # Most recent signal value
                    
                    # Calculate previous MACD and signal values for crossover detection
                    prev_macd_line = macd['macd'][-2]
                    prev_signal_line = macd['signal'][-2]

                    # Check buy condition: MACD line crosses above the signal line
                    if prev_macd_line <= prev_signal_line and macd_line > signal_line:
                        allocation_dict[ticker] = self.initial_investment / len(self.tickers)

                    # Check sell condition: Signal line crosses above the MACD line
                    elif prev_signal_line <= prev_macd_line and signal_line > macd_line:
                        allocation_dict[ticker] = 0

            except Exception:
                # Handle exceptions silently
                pass

        return TargetAllocation(allocation_dict)