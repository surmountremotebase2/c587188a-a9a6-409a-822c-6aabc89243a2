from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SO
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        self.observation_window = 14  # Typical period for Stochastic Oscillator

    @property
    def interval(self):
        return "1day"  # Interval for data observation, adjust as needed

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}

        for ticker in self.tickers:
            ohlcv = data["ohlcv"]
            # Calculate the Stochastic Oscillator for each stock
            so_values = SO(ticker, ohlcv, self.observation_window)
            if so_values is None:
                continue

            # Current and Previous %K and %D values
            k_curr, d_curr = so_values["K"][-1], so_values["D"][-1]
            k_prev, d_prev = so_values["K"][-2], so_values["D"][-2]

            # Enter Position Logic: %K crosses above %D in the oversold region
            if k_prev < d_prev and k_curr > d_curr and k_curr < 20:
                allocation_dict[ticker] = 1.0 / len(self.tickers)  # Equal allocation
            
            # Liquidate Position Logic: %K crosses below %D in the overbought region
            elif k_prev > d_prev and k_curr < d_curr and k_curr > 80:
                allocation_dict[ticker] = 0  # Move out of position
            else:
                # Maintain existing position decisions if no entry or exit signal
                allocation_dict[ticker] = allocation_dict.get(ticker, 0)

        return TargetAllocation(allocation_dict)