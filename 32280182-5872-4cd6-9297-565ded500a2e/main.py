from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, ADX, ATR, CCI, BB, MFI, RSI
from .macd import MACD  # Import custom MACD from macd.py
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

                # Initialize allocation for each ticker
                current_allocation = 0.0  # Default allocation is 0, meaning no position

                # Buy Conditions
                if macd_line and signal_line:
                    if (macd_line[-1] > signal_line[-1]) and (ema21[-1] > ema9[-1]):  # Buy condition 1
                        current_allocation = 1/9  # Allocate 1/9 of capital for each stock

                    elif (rsi and rsi[-1] > 65 or (mfi and mfi[-1] < 20)) and (adx and adx[-1] > 60):  # Buy condition 2
                        current_allocation = 1/9

                    elif (cci and cci[-1] > 100) and (atr and atr[-1] > 0.6) and (mfi and mfi[-1] < 20):  # Buy condition 3
                        current_allocation = 1/9

                    elif (bb and bb["lower"][-1] < close_prices[-1]) and (rsi and rsi[-1] < 30) and (adx and adx[-1] > 60) and (cci and cci[-1] < -100):  # Buy condition 4
                        current_allocation = 1/9

                # Sell Conditions
                if macd_line and signal_line:
                    if (signal_line[-1] > macd_line[-1]) and (ema9[-1] > ema21[-1]):  # Sell condition 1
                        current_allocation = 0.0  # Sell the position

                    elif (rsi and rsi[-1] < 35 or (mfi and mfi[-1] > 80)) and (adx and adx[-1] > 60):  # Sell condition 2
                        current_allocation = 0.0

                    elif (cci and cci[-1] < -100) and (atr and atr[-1] > 0.6):  # Sell condition 3
                        current_allocation = 0.0

                    elif (bb and bb["upper"][-1] > close_prices[-1]) and (rsi and rsi[-1] > 70):  # Sell condition 4
                        current_allocation = 0.0

                    elif (atr and atr[-1] > 0.7 and adx and adx[-1] > 70) and (atr[-1] > 0.75 or adx[-1] > 75) and (cci and cci[-1] > 100):  # Sell condition 5
                        current_allocation = 0.0

                # Check stop loss: Example condition based on ATR
                stop_loss_trigger = False
                if atr and atr[-1] > 0.6:
                    stop_loss_trigger = True

                # Apply stop loss if triggered
                if stop_loss_trigger:
                    current_allocation = 0.0  # Sell position if stop-loss is triggered

                # Update allocation dictionary for the ticker
                allocation_dict[ticker] = current_allocation

                # Log technical indicators and allocation
                log(f"{ticker} Allocation: {current_allocation}, "
                    f"MACD: {macd_line[-1] if macd_line else 'N/A'}, Signal: {signal_line[-1] if signal_line else 'N/A'}, "
                    f"EMA9: {ema9[-1] if ema9 else 'N/A'}, EMA21: {ema21[-1] if ema21 else 'N/A'}, "
                    f"RSI: {rsi[-1] if rsi else 'N/A'}, ADX: {adx[-1] if adx else 'N/A'}, ATR: {atr[-1] if atr else 'N/A'}, "
                    f"CCI: {cci[-1] if cci else 'N/A'}, BB Lower: {bb['lower'][-1] if bb else 'N/A'}, "
                    f"BB Upper: {bb['upper'][-1] if bb else 'N/A'}, MFI: {mfi[-1] if mfi else 'N/A'}")

        # Return target allocation to be used by the strategy
        return TargetAllocation(allocation_dict)