from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["AAPL", "NVDA", "MSFT", "AMD", "META"]

    @property
    def interval(self):
        # Choosing 1day as trading decision interval for simplicity
        return "1day"

    @property
    def assets(self):
        # Assets that we are interested in
        return self.tickers

    def run(self, data):
        allocation_dict = {}

        for ticker in self.tickers:
            ema9 = EMA(ticker, data, 9)[-1]
            ema21 = EMA(ticker, data, 21)[-1]
            rsi = RSI(ticker, data, 4)[-1]
            macd_info = MACD(ticker, data, 8, 17, 9)
            macd_line = macd_info['MACD'][-1] if 'MACD' in macd_info else 0
            signal_line = macd_info['signal'][-1] if 'signal' in macd_info else 0

            # Trade entry conditions
            if ema9 > ema21 and rsi > 60 and macd_line > signal_line:
                allocation_dict[ticker] = 1 / len(self.tickers)

            # Trade exit / liquidate conditions
            elif ema21 > ema9 and rsi < 45 and macd_line < signal_line:
                allocation_dict[ticker] = 0

            # If none of the conditions match, do not allocate
            else:
                allocation_dict[ticker] = 0

        # Logging for debugging purposes, to observe the decisions being taken
        log(f"Allocation: {allocation_dict}")
        
        return TargetAllocation(allocation_dict)