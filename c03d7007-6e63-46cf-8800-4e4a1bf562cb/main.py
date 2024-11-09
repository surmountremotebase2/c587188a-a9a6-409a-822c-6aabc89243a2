from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, SMA, BB, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "TSLA", "META"]
        # No need to include OHLCV data in data_list explicitly, it's automatically included

    @property
    def interval(self):
        # Choose an interval suitable for your trading style (e.g., "1day" for daily strategy)
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            # Calculate technical indicators for each ticker
            rsi = RSI(ticker, data["ohlcv"], length=14)
            ema = EMA(ticker, data["ohlcv"], length=20)
            sma = SMA(ticker, data["ohlcv"], length=50)
            bb = BB(ticker, data["ohlcv"], length=20, std=2)  # Standard deviation for BBs
            atr = ATR(ticker, data["ohlcv"], length=14)
            
            # Log the last values for each indicator to inspect their output
            log(f"{ticker} RSI: {rsi[-1] if rsi else 'N/A'}, EMA: {ema[-1] if ema else 'N/A'}, SMA: {sma[-1] if sma else 'N/A'}, BB Lower: {bb['lower'][-1] if bb else 'N/A'}, BB Upper: {bb['upper'][-1] if bb else 'N/A'}, ATR: {atr[-1] if atr else 'N/A'}")
            
            # Define simple trading logic based on technical indicators
            current_allocation = 0.0  # Default to holding no position
            if rsi and rsi[-1] < 30 and ema[-1] > sma[-1]:  # Basic example criteria for buying
                current_allocation = 1/3  # Equal weight to each ticker for simplicity

            # Update allocation dictionary
            allocation_dict[ticker] = current_allocation

        return TargetAllocation(allocation_dict)