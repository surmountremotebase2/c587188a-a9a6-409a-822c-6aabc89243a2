from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, ATR, ADX, CCI, BB, MFI  # Add any other indicators as needed
from macd import MACD  # Import the MACD function from macd.py
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        allocations = {ticker: 0.0 for ticker in self.tickers}

        for ticker in self.tickers:
            if len(data["ohlcv"]) > 26:  # Ensuring enough data for MACD and other indicators

                close_prices = [entry[ticker]["close"] for entry in data["ohlcv"]]
                ema9 = EMA(ticker, data["ohlcv"], length=9)
                ema21 = EMA(ticker, data["ohlcv"], length=21)
                macd_line, signal_line = MACD(close_prices, 12, 26, 9)  # Using MACD from macd.py
                rsi = RSI(ticker, data["ohlcv"], length=14)
                atr = ATR(ticker, data["ohlcv"], length=14)
                adx = ADX(ticker, data["ohlcv"], length=14)
                cci = CCI(ticker, data["ohlcv"], length=14)
                mfi = MFI(ticker, data["ohlcv"], length=14)
                bb_lower, bb_upper = BB(ticker, data["ohlcv"], length=20, std_dev=2)

                # Get the latest values for the indicators
                current_close = close_prices[-1]
                current_ema9 = ema9[-1] if ema9 else None
                current_ema21 = ema21[-1] if ema21 else None
                current_macd = macd_line[-1] if macd_line else None
                current_signal = signal_line[-1] if signal_line else None
                current_rsi = rsi[-1] if rsi else None
                current_atr = atr[-1] if atr else None
                current_adx = adx[-1] if adx else None
                current_cci = cci[-1] if cci else None
                current_mfi = mfi[-1] if mfi else None
                current_bb_lower = bb_lower[-1] if bb_lower else None
                current_bb_upper = bb_upper[-1] if bb_upper else None

                # Buy conditions
                buy_conditions = [
                    current_macd > current_signal,
                    current_ema21 - current_ema9 > 1,
                    current_rsi > 65 or current_mfi < 20,
                    current_adx > 60,
                    current_cci > 100,
                    current_atr > 0.6,
                    current_close < current_bb_lower and current_rsi < 30 and current_cci < -100
                ]

                # Sell conditions
                sell_conditions = [
                    current_signal > current_macd,
                    current_ema9 - current_ema21 > 1,
                    current_rsi < 35 or current_mfi > 80,
                    current_cci < -100,
                    current_atr > 0.6,
                    current_adx > 60,
                    current_close > current_bb_upper and current_rsi > 70 and (current_atr > 0.7 or current_adx > 70)
                ]

                # Decide allocation
                if all(buy_conditions[:6]):
                    allocations[ticker] = 1.0
                    log(f"Buy signal for {ticker}: EMA9: {current_ema9}, EMA21: {current_ema21}, MACD: {current_macd}, Signal: {current_signal}, RSI: {current_rsi}, ADX: {current_adx}, CCI: {current_cci}, ATR: {current_atr}")
                elif all(sell_conditions[:6]):
                    allocations[ticker] = -1.0
                    log(f"Sell signal for {ticker}: EMA9: {current_ema9}, EMA21: {current_ema21}, MACD: {current_macd}, Signal: {current_signal}, RSI: {current_rsi}, ADX: {current_adx}, CCI: {current_cci}, ATR: {current_atr}")

        return TargetAllocation(allocations)