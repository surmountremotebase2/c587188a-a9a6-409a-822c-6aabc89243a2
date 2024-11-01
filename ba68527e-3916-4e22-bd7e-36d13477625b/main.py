from surmount.base_class import Strategy, TargetAllocation
from surmount.data import OHLCV
from surmount.technical_indicators import EMA

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        self.capital = 3000  # Total capital to invest
        self.ema_short_period = 9
        self.ema_long_period = 21

    @property
    def interval(self):
        return "1hour"

    @property
    def assets(self):
        return self.tickers

    @property
    def data_list(self):
        # We only need OHLCV data for technical indicators, which are computed internally
        return []

    def run(self, data):
        allocation_dict = {}
        total_investment = 0

        for ticker in self.tickers:
            ohlcv_data = data["ohlcv"][ticker]

            # Compute EMA for both short and long periods
            ema_short = EMA(ticker, ohlcv_data, length=self.ema_short_period)
            ema_long = EMA(ticker, ohlcv_data, length=self.ema_long_period)

            # Ensure we have enough data points for both EMAs
            if len(ema_short) > 0 and len(ema_long) > 0:
                last_ema_short = ema_short[-1]
                last_ema_long = ema_long[-1]

                # If EMA9 > EMA21, set allocation proportional to the capital
                if last_ema_short > last_ema_long:
                    allocation_dict[ticker] = self.capital / len(self.tickers)
                    total_investment += allocation_dict[ticker]
                else:
                    allocation_dict[ticker] = 0
            else:
                allocation_dict[ticker] = 0

        # Adjust allocations to maintain total investment under or equal to self.capital
        if total_investment > 0:
            for ticker in allocation_dict:
                allocation_dict[ticker] = (allocation_dict[ticker] / total_investment) * self.capital

        return TargetAllocation(allocation_dict)