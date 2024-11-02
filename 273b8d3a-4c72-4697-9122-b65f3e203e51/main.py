#Type code here
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define tickers for the strategy
        self.tickers = ["TSLA", "AAPL", "MSFT"]
        # Initial allocation dict to track position for each asset 
        self.allocation_dict = {ticker: 0 for ticker in self.tickers}
        self.entry_price = {ticker: 0 for ticker in self.tickers}  # Store entry prices for stop-loss calculations

    @property
    def interval(self):
        # Use 1-hour interval for the strategy
        return "1hour"

    @property
    def assets(self):
        # Return the list of tickers
        return self.tickers

    def run(self, data):
        # Iterate through tickers to apply the strategy
        for ticker in self.tickers:
            ohlcv = data["ohlcv"][ticker]
            ema9 = EMA(ticker, ohlcv, length=9)[-1]  # Latest EMA9
            ema21 = EMA(ticker, ohlcv, length=21)[-1]  # Latest EMA21
            atr = ATR(ticker, ohlcv, length=14)[-1]  # Latest ATR
            
            # Check for entry condition
            if ema9 > ema21:
                if self.allocation_dict[ticker] == 0:  # Not already in position
                    self.entry_price[ticker] = ohlcv[-1]['close']  # Record entry price
                    self.allocation_dict[ticker] = 1.0 / len(self.tickers)  # Allocate equally among assets
                    log(f"Initial buy for {ticker} at {self.entry_price[ticker]}")

            # Check for exit condition
            elif ema21 > ema9:
                if self.allocation_dict[ticker] > 0:  # Already in position
                    self.allocation_dict[ticker] = 0  # Liquidate position
                    log(f"Liquidate position for {ticker} as EMA21 is greater than EMA9")

            # Implementing stop-loss
            if self.allocation_dict[ticker] > 0:  # In position
                stop_loss_price = self.entry_price[ticker] * 0.9  # 10% stop-loss
                if ohlcv[-1]['close'] < stop_loss_price:
                    self.allocation_dict[ticker] = 0  # Liquidate position at stop-loss
                    log(f"Stop-loss triggered for {ticker}. Liquidating position.")

        return TargetAllocation(self.allocation_dict)

def log(message):
    print(message)  # Replace this with a logging framework as needed