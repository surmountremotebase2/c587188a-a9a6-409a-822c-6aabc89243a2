from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]

    @property
    def interval(self):
        return "1day"   # Adjust the interval as needed

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            try:
                macd_data = MACD(ticker, data["ohlcv"], fast=12, slow=26)  # default MACD settings (fast=12, slow=26)
                if len(macd_data["MACD"]) >= 2 and len(macd_data["signal"]) >= 2:
                    macd_line_last = macd_data["MACD"][-1]
                    macd_line_prev = macd_data["MACD"][-2]
                    signal_line_last = macd_data["signal"][-1]
                    signal_line_prev = macd_data["signal"][-2]
                    
                    # Decision: MACD line crosses above signal line
                    if macd_line_last > signal_line_last and macd_line_prev <= signal_line_prev:
                        allocation_dict[ticker] = 1.0 / len(self.tickers)  # Allocate evenly among tickers
                    # Decision: MACD line crosses below signal line
                    elif macd_line_last < signal_line_last and macd_line_prev >= signal_line_prev:
                        allocation_dict[ticker] = 0  # Liquidate position
                    else:
                        allocation_dict[ticker] = 0  # No action/hold
                else:
                    allocation_dict[ticker] = 0  # Default to no allocation if insufficient data
            except Exception as e:
                log(f"Error processing {ticker}: {str(e)}")
                allocation_dict[ticker] = 0  # Default to no allocation on error
                
        return TargetAllocation(allocation_dict)