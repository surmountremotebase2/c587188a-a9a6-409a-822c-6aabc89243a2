from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, ATR, ADX, CCI, BB, MFI  # Import necessary indicators
from macd import MACD  # Ensure macd.py contains MACD function and is in the same directory or package
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
            if len(data["ohlcv"]) > 26:  # Check for enough data for MACD and other indicators
                # Fetch price and indicator values for the ticker
                close_prices = [entry[ticker]["close"] for entry in data["ohlcv"]]
                ema9 = EMA(ticker, data["ohlcv"], length=9)
                ema21 = EMA(ticker, data["ohlcv"], length=21)
                macd_line, signal_line = MACD(close_prices, 12, 26, 9)
                rsi = RSI(ticker, data["ohlcv"], length=14)
                atr = ATR(ticker, data["ohlcv"], length=14)
                adx = ADX(ticker, data["ohlcv"], length=14)
                cci = CCI(ticker, data["ohlcv"], length=14)
                mfi = MFI(ticker, data["ohlcv"], length=14)

                # Adjust BB call here based on available arguments
                bb_values = BB(ticker, data["ohlcv"], length=20)  # Assuming BB returns both lower and upper bands
                if bb_values and len(bb_values[-1]) == 2:
                    bb_lower, bb_upper = bb_values[-1]
                else:
                    bb_lower, bb_upper = None, None

                # Retrieve the latest values for each indicator
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

                # Buy conditions
                buy_conditions = [
                    current_macd > current_signal,                          # MACD line crosses above signal line
                    (current_ema21 - current_ema9) > 1,                    # EMA21 stays above EMA9 with a difference > 1
                    (current_rsi > 65 or current_mfi < 20),                # RSI > 65 or MFI < 20
                    current_adx > 60,                                      # ADX > 60
                    current_cci > 100,                                     # CCI > 100
                    current_atr > 0.6,                                     # ATR > 0.6
                    bb_lower and current_close < bb_lower and current_rsi < 30 and current_cci < -100  # Price below BB lower band, RSI < 30, CCI < -100
                ]

                # Sell conditions
                sell_conditions = [
                    current_signal > current_macd,                         # Signal line crosses above MACD line
                    (current_ema9 - current_ema21) > 1,                    # EMA9 stays above EMA21 with a difference > 1
                    (current_rsi < 35 or current_mfi > 80),                # RSI < 35 or MFI > 80
                    current_cci < -100,                                    # CCI < -100
                    current_atr > 0.6,                                     # ATR > 0.6
                    current_adx > 60,                                      # ADX > 60
                    bb_upper and current_close > bb_upper and current_rsi > 70 and (current_atr > 0.7 or current_adx > 70)  # Price above BB upper band, RSI > 70, and either ATR > 0.7 or ADX > 70
                ]

                # Allocate based on buy/sell conditions
                if all(buy_conditions[:6]):
                    allocations[ticker] = 1.0
                    log(f"Buy signal for {ticker}: MACD={current_macd}, Signal={current_signal}, EMA9={current_ema9}, EMA21={current_ema21}, RSI={current_rsi}, MFI={current_mfi}, ADX={current_adx}, CCI={current_cci}, ATR={current_atr}")

                elif all(sell_conditions[:6]):
                    allocations[ticker] = -1.0
                    log(f"Sell signal for {ticker}: MACD={current_macd}, Signal={current_signal}, EMA9={current_ema9}, EMA21={current_ema21}, RSI={current_rsi}, MFI={current_mfi}, ADX={current_adx}, CCI={current_cci}, ATR={current_atr}")

                # Stop-loss check
                if current_atr and allocations[ticker] > 0 and (current_close <= current_close - current_atr):
                    allocations[ticker] = -1.0  # Trigger stop-loss to sell holdings
                    log(f"Stop-loss triggered for {ticker} at price: {current_close}, ATR: {current_atr}")

        return TargetAllocation(allocations)