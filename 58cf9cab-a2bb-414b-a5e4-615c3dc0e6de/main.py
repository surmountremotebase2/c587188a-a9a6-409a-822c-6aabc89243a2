from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        # Assuming an equally divided investment strategy across tickers for simplicity
        self.investment_per_ticker = 3000 / len(self.tickers)

    @property
    def interval(self):
        # Using daily interval for MACD calculation
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            if ticker in data["ohlcv"]:
                # Calculate MACD for the ticker
                macd_data = MACD(ticker, data["ohlcv"], fast=12, slow=26)
                if macd_data is not None:
                    # MACD and Signal lines
                    macd_line = macd_data["MACD"][-1]  # Current MACD value
                    signal_line = macd_data["signal"][-1]  # Current signal value
                    baseline = 0  # Assuming 0 as the baseline for crossover

                    # Determine buy or sell
                    if macd_line > signal_line and macd_line < baseline:
                        # Buy condition: MACD crosses above signal line below baseline
                        allocation_dict[ticker] = self.allocate_investment(ticker)
                    elif signal_line > macd_line and signal_line > baseline:
                        # Sell condition: Signal line crosses above MACD line above baseline
                        allocation_dict[ticker] = 0  # Liquidate position
                else:
                    log(f"MACD calculation failed for {ticker}, skipping allocation.")
            else:
                log(f"No OHLCV data for {ticker}, skipping allocation.")

        # This example does not explicitly calculate actual share amounts to be allocated per ticker
        # or manage the specifics of dividing the $3000 investment.
        # The allocation here is symbolic and requires integration with actual trading commands
        return TargetAllocation(allocation_dict)

    def allocate_investment(self, ticker):
        # Simplified representation, should be replaced with actual allocation logic
        # based on current asset price to determine share count.
        return 1 / len(self.tickers)  # Equally divided for example purposes