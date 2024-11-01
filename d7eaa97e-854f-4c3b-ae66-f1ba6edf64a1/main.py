from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers to be traded
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        
        # Initialize variables to keep track of the allocation
        self.allocation = {ticker: 0 for ticker in self.tickers}

    @property
    def assets(self):
        # The assets that we are interested in
        return self.tickers

    @property
    def interval(self):
        # Use 1-hour interval for MACD calculation
        return "1hour"

    def run(self, data):
        # Iterate through each ticker to calculate the MACD and decide on the allocation
        for ticker in self.tickers:
            # Check if there's enough data for MACD calculation
            if len(data["ohlcv"]) > 35:  # Considering MACD typical settings (12,26,9) might need at least 35 periods
                macd_data = MACD(ticker, data["ohlcv"], fast=12, slow=26)
                # If MACD data calculation was successful
                if macd_data is not None:
                    # Get the latest MACD and signal values
                    macd_line = macd_data["MACD"][-1]
                    signal_line = macd_data["signal"][-1]

                    # Decision to invest or liquidate
                    if macd_line > signal_line:
                        self.allocation[ticker] = 1.0 / len(self.tickers)  # Invest equally among the tickers
                    else:
                        self.allocation[ticker] = 0  # Liquidate
                else:
                    log(f"MACD data unavailable for {ticker}, keeping previous allocation.")
            else:
                log(f"Not enough data for calculating MACD for {ticker}, skipping.")

        # Return the target allocation based on the MACD strategy
        return TargetAllocation(self.allocation)

# Note that in order to execute this strategy in real or simulated trading environments,
# it needs to be integrated within the Surmount trading framework which will handle data fetching,
# order execution, and strategy lifecycle. The strategy assumes equal-weight allocation across assets
# when conditions are met without considering transaction costs or slippage.