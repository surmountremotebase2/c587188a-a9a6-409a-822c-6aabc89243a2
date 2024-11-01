from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.logging import log
from surmount.data import OHLCV

class TradingStrategy(Strategy):
    
    @property
    def assets(self):
        return ["AAPL"]

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        # Initialize allocation to 0
        allocation = 0
        
        # Retrieve OHLCV data for AAPL
        ohlcv_data = data['ohlcv']['AAPL']

        # Calculate EMA9 and EMA21
        ema9 = EMA("AAPL", ohlcv_data, 9)
        ema21 = EMA("AAPL", ohlcv_data, 21)
        
        # Calculate MACD with its signal line
        macd = MACD("AAPL", ohlcv_data, 12, 26)['MACD']
        signal_line = MACD("AAPL", ohlcv_data, 12, 26)['signal']

        # Calculate RSI with 4 periods
        rsi = RSI("AAPL", ohlcv_data, 4)
        
        # Check if the data points are available
        if len(ema9) > 0 and len(ema21) > 0 and len(rsi) > 0 and len(macd) > 0 and len(signal_line) > 0:
            # The condition to open a long position: EMA9 > EMA21, RSI > 65, and MACD > Signal Line
            if ema9[-1] > ema21[-1] and rsi[-1] > 65 and macd[-1] > signal_line[-1]:
                allocation = 1  # Invest 100% of the portfolio in AAPL
                log("Long AAPL")

            # The condition to close a long position: EMA9 < EMA21, RSI < 45, and MACD < Signal Line
            elif ema9[-1] < ema21[-1] and rsi[-1] < 45 and macd[-1] < signal_line[-1]:
                allocation = 0  # Liquidate AAPL position
                log("Exit AAPL")
        else:
            log("Insufficient data to make a decision.")
        
        return TargetAllocation({"AAPL": allocation})