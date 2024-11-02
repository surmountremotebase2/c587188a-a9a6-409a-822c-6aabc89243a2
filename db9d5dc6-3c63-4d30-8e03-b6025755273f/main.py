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
        
        # Extract MACD values and log output for inspection
        macd = MACD(ticker, ohlcv, fast=12, slow=26)
        log(f"MACD output for {ticker}: {macd}")  # Log the entire MACD output
        log(macd)  # Log the output to check the keys

         # Check for keys in the MACD output
        if 'macd' in macd and 'signal' in macd:
            macd_line = macd['macd'][-1]  # Access the last MACD value
            signal_line = macd['signal'][-1]  # Access the last signal value
            log(f"Latest MACD for {ticker}: {macd_line}, Signal: {signal_line}")
        else:
            log(f"MACD output keys missing for {ticker}: {macd}")
            macd_line = None
            signal_line = None
            
        rsi = RSI(ticker, ohlcv, length=14)[-1]
        bb = BB(ticker, ohlcv, length=20)
        stochastic = SO(ticker, ohlcv)
        atr = ATR(ticker, ohlcv, length=14)[-1]
        obv = OBV(ticker, ohlcv)

        # Ensure macd_line and signal_line are not None before proceeding
        if macd_line is not None and signal_line is not None:
            buy_conditions = [
                ema_9 > ema_21,
                macd_line > signal_line,
                rsi < 30,
                ohlcv[-1][ticker]['close'] < bb['lower'][-1],
                stochastic['%K'][-1] > stochastic['%D'][-1],
                obv > obv[-2]
            ]

            if sum(buy_conditions) >= 5:
                allocation_dict[ticker] = 1 / len(self.tickers)

            sell_conditions = [
                ema_9 < ema_21,
                macd_line < signal_line,
                rsi > 70,
                ohlcv[-1][ticker]['close'] > bb['upper'][-1],
                stochastic['%K'][-1] < stochastic['%D'][-1],
                ohlcv[-1][ticker]['close'] < PSAR(ticker, ohlcv)[-1],
                atr > 0
            ]

            if sum(sell_conditions) >= 7:
                allocation_dict[ticker] = 0

    return TargetAllocation(allocation_dict)