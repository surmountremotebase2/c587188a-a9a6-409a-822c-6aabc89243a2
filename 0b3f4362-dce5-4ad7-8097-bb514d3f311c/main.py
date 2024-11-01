from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        
        for ticker in self.tickers:
            macd_data = MACD(ticker, data["ohlcv"], fast=12, slow=26)
            # Ensure MACD data is present
            if macd_data is None or len(macd_data["MACD"]) < 2 or len(macd_data["signal"]) < 2:
                log(f"MACD data insufficient for {ticker}.")
                continue

            # Last two MACD and signal values to determine crossover
            last_macd = macd_data["MACD"][-1]
            prev_macd = macd_data["MACD"][-2]
            
            last_signal = macd_data["signal"][-1]
            prev_signal = macd_data["signal"][-2]
            
            # MACD line crosses above signal line - Buy signal
            if prev_macd <= prev_signal and last_macd > last_signal:
                log(f"MACD crossover buy signal for {ticker}.")
                allocation_dict[ticker] = 1.0 / len(self.tickers)
            
            # Signal line crosses above MACD line - Sell/liquidate signal
            elif prev_macd >= prev_signal and last_macd < last_signal:
                log(f"MACD crossover sell signal for {ticker}.")
                allocation_dict[ticker] = 0
            else:
                # No action, maintain previous allocation if any
                allocation_dict[ticker] = 0

        return TargetAllocation(allocation_dict)