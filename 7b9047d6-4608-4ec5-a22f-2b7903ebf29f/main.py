from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, ADX, ATR, CCI, BB, MFI, RSI
from .macd import MACD  # Import custom MACD from macd.py
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self, initial_investment=2000):
        self.tickers = [
            "AAPL", "AMZN", "META", "NFLX", "GOOG", "MSFT", "AMD", "SQ"
            #"DIS", "HD", "WMT", "BIIB", "UNH", "SHOP", "AMGN", "PEP", "XOM", "JPM", "PG", "LMT", "NOC", "CRM", "DHR", "NOW", "QQQ", "SPY", "IWM"
        ]

    @property
    def interval(self):
        return "5min"  # 1-hour interval as specified

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}

        if len(data["ohlcv"]) > 26:  # Ensure enough data for indicators
            for ticker in self.tickers:
                # Fetch OHLCV data
                ohlcv = data.get("ohlcv")
                close_prices = [entry[ticker]["close"] for entry in ohlcv]
                current_close = close_prices[-1]

                # Calculate technical indicators
                macd_line, signal_line = MACD(close_prices, fast_period=12, slow_period=26, signal_period=9)  # Custom MACD
                ema9 = EMA(ticker, ohlcv, length=9)  # EMA 9
                ema21 = EMA(ticker, ohlcv, length=21)  # EMA 21
                rsi = RSI(ticker, ohlcv, length=14)  # RSI
                adx = ADX(ticker, ohlcv, length=14)  # ADX
                atr = ATR(ticker, ohlcv, length=14)  # ATR
                cci = CCI(ticker, ohlcv, length=14)  # CCI
                bb = BB(ticker, ohlcv, length=20, std=2)  # Bollinger Bands (BB)
                mfi = MFI(ticker, ohlcv, length=14)  # Money Flow Index (MFI)

                # Get current indicator values
                current_macd = macd_line[-1] if macd_line else None
                current_signal = signal_line[-1] if signal_line else None
                previous_macd = macd_line[-2] if macd_line else None
                previous_signal = signal_line[-2] if signal_line else None
                current_ema9 = ema9[-1] if ema9 else None
                current_ema21 = ema21[-1] if ema21 else None
                current_rsi = rsi[-1] if rsi else None
                current_adx = adx[-1] if adx else None
                current_atr = atr[-1] if atr else None
                current_cci = cci[-1] if cci else None
                current_mfi = mfi[-1] if mfi else None
                bb_lower = bb["lower"][-1] if bb and "lower" in bb else None
                bb_upper = bb["upper"][-1] if bb and "upper" in bb else None

                # Log all the indicators
                log(f"Ticker: {ticker}, Close: {current_close}, MACD: {current_macd}, Signal: {current_signal}, EMA9: {current_ema9}, EMA21: {current_ema21}, "
                f"RSI: {current_rsi}, ADX: {current_adx}, ATR: {current_atr}, CCI: {current_cci}, MFI: {current_mfi}, BB Lower: {bb_lower}, BB Upper: {bb_upper}")
        # Return target allocation to be used by the strategy
        return TargetAllocation(allocation_dict)