from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, ADX, ATR, CCI, BB, MFI, RSI
from macd import MACD  # Import custom MACD from macd.py
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]
    
    @property
    def interval(self):
        return "1hour"  # 1-hour interval as specified

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
                current_ema9 = ema9[-1] if ema9 else None
                current_ema21 = ema21[-1] if ema21 else None
                current_rsi = rsi[-1] if rsi else None
                current_adx = adx[-1] if adx else None
                current_atr = atr[-1] if atr else None
                current_cci = cci[-1] if cci else None
                current_mfi = mfi[-1] if mfi else None
                bb_lower = bb["lower"][-1] if bb and "lower" in bb else None
                bb_upper = bb["upper"][-1] if bb and "upper" in bb else None

                # Buy Conditions
                buy_conditions = [
                    current_macd > current_signal,                          # MACD line crosses above signal line
                    (current_ema21 - current_ema9) > 1,                    # EMA21 stays above EMA9 with a difference > 1
                    (current_rsi > 65 or current_mfi < 20),                # RSI > 65 or MFI < 20
                    current_adx > 60,                                      # ADX > 60
                    current_cci > 100,                                     # CCI > 100
                    current_atr > 0.6,                                     # ATR > 0.6
                    bb_lower and current_close < bb_lower and current_rsi < 30 and current_cci < -100  # Price below BB lower band, RSI < 30, CCI < -100
                ]

                # Sell Conditions
                sell_conditions = [
                    current_signal > current_macd,                         # Signal line crosses above MACD line
                    (current_ema9 - current_ema21) > 1,                    # EMA9 stays above EMA21 with a difference > 1
                    (current_rsi < 35 or current_mfi > 80),                # RSI < 35 or MFI > 80
                    current_cci < -100,                                    # CCI < -100
                    current_atr > 0.6,                                     # ATR > 0.6
                    current_adx > 60,                                      # ADX > 60
                    bb_upper and current_close > bb_upper and current_rsi > 70 and (current_atr > 0.7 or current_adx > 70)  # Price above BB upper band, RSI > 70, and either ATR > 0.7 or ADX > 70
                ]

                # Count how many buy conditions are met
                buy_conditions_met = sum([1 for condition in buy_conditions if condition])

                # Count how many sell conditions are met
                sell_conditions_met = sum([1 for condition in sell_conditions if condition])

                # Check if 2 or more buy conditions are met
                if buy_conditions_met >= 1:
                    allocation_dict[ticker] = 1/9  # Allocate 1/9 of capital for each stock
                    log(f"Buying {ticker} based on {buy_conditions_met} buy conditions met")
                    log(f"Buy signal for {ticker}: MACD={current_macd}, Signal={current_signal}, EMA9={current_ema9}, EMA21={current_ema21}, RSI={current_rsi}, MFI={current_mfi}, ADX={current_adx}, CCI={current_cci}, ATR={current_atr}")

                # Check if 2 or more sell conditions are met
                elif sell_conditions_met >= 1:
                    allocation_dict[ticker] = 0.0  # Sell the position
                    log(f"Selling {ticker} based on {sell_conditions_met} sell conditions met")
                    log(f"Sell signal for {ticker}: MACD={current_macd}, Signal={current_signal}, EMA9={current_ema9}, EMA21={current_ema21}, RSI={current_rsi}, MFI={current_mfi}, ADX={current_adx}, CCI={current_cci}, ATR={current_atr}")

                # Stop-loss condition example (based on ATR)
                stop_loss_trigger = False
                if current_atr > 0.6:
                    stop_loss_trigger = True

                # Apply stop loss if triggered
                if stop_loss_trigger:
                    allocation_dict[ticker] = 0.0  # Sell position if stop-loss is triggered
                    log(f"Selling {ticker} due to stop-loss being triggered")

        # Return target allocation to be used by the strategy
        return TargetAllocation(allocation_dict)