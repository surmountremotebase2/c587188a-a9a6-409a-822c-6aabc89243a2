from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, ADX, ATR, CCI, BB, MFI, RSI
from .macd import MACD  # Import custom MACD from macd.py
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]
        self.holding_dict = {ticker: 0 for ticker in self.tickers}  # Initialize holding_dict to track positions
    
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

                # Buy Conditions
                if macd_line and signal_line:
                    if previous_signal > previous_macd and current_macd > current_signal and (current_macd - current_signal) < 0 and current_rsi < 40 and current_mfi < 20 and current_adx > 40 and current_cci < 0:  # Buy condition 1
                        allocation_dict[ticker] = 1/9  # Allocate 1/9 of capital for each stock
                        self.entry_prices[ticker] = current_close  # Track entry price for stop-loss
                        log(f"Buy signal for {ticker}: MACD={current_macd}, Signal={current_signal}, EMA9={current_ema9}, EMA21={current_ema21}, RSI={current_rsi}, MFI={current_mfi}, ADX={current_adx}, CCI={current_cci}, ATR={current_atr}")

                    #elif (current_ema21 > current_ema9) and current_rsi < 35:  # Buy condition 2
                        #allocation_dict[ticker] = 1/9
                        #log(f"Buy signal for {ticker}: current_ema21 > current_ema9) and current_rsi < 35 : EMA9={current_ema9}, EMA21={current_ema21}, RSI=#{current_rsi}, MFI={current_mfi}, ADX={current_adx}, CCI={current_cci}, ATR={current_atr}")

                    #elif (current_rsi > 65 or current_mfi < 20):  # Buy condition 3
                        #allocation_dict[ticker] = 1/9
                        #log(f"Buy signal for {ticker}: RSI > 65 or MFI < 20: RSI={current_rsi}, MFI={current_mfi}, EMA9={current_ema9}, EMA21={current_ema21}, #ADX={current_adx}, CCI={current_cci}, ATR={current_atr}")

                    #elif current_adx > 60 and current_cci > 100 and current_atr > 0.6:  # Buy condition 4
                        #allocation_dict[ticker] = 1/9
                        #log(f"Buy signal for {ticker}: ADX > 60, CCI > 100, ATR > 0.6: ADX={current_adx}, CCI={current_cci}, ATR={current_atr}, EMA9={current_ema9}, EMA21={current_ema21}, RSI={current_rsi}, MFI={current_mfi}")

                    elif bb_lower and current_close < bb_lower and current_rsi < 35 and current_mfi < 20 and current_adx > 40 and current_cci < -150:  # Buy condition 5
                        allocation_dict[ticker] = 1/9
                        self.entry_prices[ticker] = current_close  # Track entry price for stop-loss
                        log(f"Buy signal for {ticker}: Price below BB lower band, RSI < 30: Close={current_close}, BB Lower={bb_lower}, RSI={current_rsi}, EMA9={current_ema9}, EMA21={current_ema21}")

                # Sell Conditions
                if macd_line and signal_line and self.holding_dict[ticker] > 0:
                    if (current_signal > current_macd) and (previous_macd > previous_signal) and (current_signal - current_macd) > 0 and current_rsi > 60 and current_mfi > 60 and current_adx > 40 and current_cci > 0:  # Sell condition 1
                        allocation_dict[ticker] = 0.0  # Sell the position
                        log(f"Sell signal for {ticker}: Signal > MACD: MACD={current_macd}, Signal={current_signal}, EMA9={current_ema9}, EMA21={current_ema21}, RSI={current_rsi}, MFI={current_mfi}, ADX={current_adx}, CCI={current_cci}, ATR={current_atr}")

                    #elif (current_ema9 > current_ema21) and current_mfi < 34:  # Sell condition 2
                        #allocation_dict[ticker] = 0.0
                        #log(f"Sell signal for {ticker}: EMA9 > EMA21 by more than 1: EMA9={current_ema9}, EMA21={current_ema21}, RSI={current_rsi}, MFI={current_mfi}, ADX={current_adx}, CCI={current_cci}, ATR={current_atr}")

                    #elif (current_rsi < 35 or current_mfi > 80):  # Sell condition 3
                        #allocation_dict[ticker] = 0.0
                        #log(f"Sell signal for {ticker}: RSI < 35 or MFI > 80: RSI={current_rsi}, MFI={current_mfi}, EMA9={current_ema9}, EMA21={current_ema21}, ADX={current_adx}, CCI={current_cci}, ATR={current_atr}")

                    #elif current_cci < -100:  # Sell condition 4
                        #allocation_dict[ticker] = 0.0
                        #log(f"Sell signal for {ticker}: CCI < -100: CCI={current_cci}, EMA9={current_ema9}, EMA21={current_ema21}, RSI={current_rsi}, MFI={current_mfi}, ADX={current_adx}, ATR={current_atr}")

                    elif bb_upper and current_close > bb_upper and current_rsi > 65 and current_mfi > 70 and current_adx > 40 and current_cci > 150:  # Sell condition 5
                        allocation_dict[ticker] = 0.0
                        log(f"Sell signal for {ticker}: Price above BB upper band, RSI > 70, ATR > 0.7 or ADX > 70: Close={current_close}, BB Upper={bb_upper}, RSI={current_rsi}, ATR={current_atr}, ADX={current_adx}, EMA9={current_ema9}, EMA21={current_ema21}")

                    # Stop-loss condition: Liquidate if price drops below entry price by 1 ATR
                    if current_close < self.entry_prices[ticker] - current_atr:
                        allocation_dict[ticker] = 0.0  # Liquidate position
                        log(f"Stop-loss triggered for {ticker}: Current price={current_close}, Entry price={self.entry_prices[ticker]}, ATR={current_atr}")

        # Return target allocation to be used by the strategy
        return TargetAllocation(allocation_dict)