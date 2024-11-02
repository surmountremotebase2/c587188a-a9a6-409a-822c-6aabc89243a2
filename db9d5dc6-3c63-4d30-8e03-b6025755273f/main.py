from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.technical_indicators import EMA, MACD, RSI, BB, SO, ATR, PSAR, OBV

class TradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        self.data_list = []

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        ohlcv = data.get("ohlcv")
        
        for ticker in self.tickers:
            ema_9 = EMA(ticker, ohlcv, 9)[-1]
            ema_21 = EMA(ticker, ohlcv, 21)[-1]
            
            # Extract MACD values correctly
            macd = MACD(ticker, ohlcv, fast=12, slow=26)
            macd_line = macd['macd'][-1]  # Get the most recent MACD value
            signal_line = macd['signal'][-1]  # Get the most recent signal line value

            rsi = RSI(ticker, ohlcv, length=14)[-1]
            bb = BB(ticker, ohlcv, length=20)
            stochastic = SO(ticker, ohlcv)
            atr = ATR(ticker, ohlcv, length=14)[-1]
            obv = OBV(ticker, ohlcv)

            buy_conditions = [
                ema_9 > ema_21,                        # EMA condition
                macd_line > signal_line,               # MACD condition (correctly references macd_line and signal_line)
                rsi < 30,                              # RSI condition
                ohlcv[-1][ticker]['close'] < bb['lower'][-1],  # Bollinger Bands condition
                stochastic['%K'][-1] > stochastic['%D'][-1],    # Stochastic condition
                obv > obv[-2]                          # OBV condition
            ]

            if sum(buy_conditions) >= 5:  # Check if at least 5 out of 6 conditions are met
                allocation_dict[ticker] = 1 / len(self.tickers)  # Equal allocation for all assets

            sell_conditions = [
                ema_9 < ema_21,                         # EMA condition
                macd_line < signal_line,                # MACD condition
                rsi > 70,                               # RSI condition
                ohlcv[-1][ticker]['close'] > bb['upper'][-1],  # Bollinger Bands condition
                stochastic['%K'][-1] < stochastic['%D'][-1],     # Stochastic condition
                ohlcv[-1][ticker]['close'] < PSAR(ticker, ohlcv)[-1],  # Parabolic SAR condition
                atr > 0                                 # ATR condition for volatility check
            ]

            if sum(sell_conditions) >= 7:  # Check if at least 7 out of 8 conditions are met
                allocation_dict[ticker] = 0  # Liquidate the position

        return TargetAllocation(allocation_dict)