from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, SMA, EMA, BB, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    
    @property
    def assets(self):
        return ["AAPL"]  # Example for a single asset; can be extended to multiple.

    @property
    def interval(self):
        return "1day"  # Interval for the indicators and asset data.
    
    def run(self, data):
        closing_prices = [i["AAPL"]["close"] for i in data["ohlcv"]]
        current_price = closing_prices[-1]

        # Calculate indicators
        rsi = RSI("AAPL", data["ohlcv"], 14)[-1]
        sma = SMA("AAPL", data["ohlcv"], 20)[-1]
        ema = EMA("AAPL", data["ohlcv"], 20)[-1]
        bb = BB("AAPL", data["ohlcv"], 20, 2)
        atr = ATR("AAPL", data["ohlcv"], 14)[-1]
        
        # Log the indicators for analysis
        log(f"RSI: {rsi}, SMA: {sma}, EMA: {ema}, BB Lower: {bb['lower'][-1]}, BB Upper: {bb['upper'][-1]}, ATR: {atr}")
        
        # Define the buy condition
        if rsi < 30 and current_price > sma and current_price < ema and current_price < bb["lower"][-1]:
            allocation = 1  # 100% allocation
            log("Buying condition met")
        # Full sell condition could be the opposite or any exit strategy
        elif rsi > 70 or current_price > bb["upper"][-1]:
            allocation = 0  # 0% allocation (exit position)
            log("Selling condition met")
        else:
            allocation = 0  # or keep the previous allocation if you track that state
            log("Holding/Exiting position")
        
        return TargetAllocation({"AAPL": allocation})