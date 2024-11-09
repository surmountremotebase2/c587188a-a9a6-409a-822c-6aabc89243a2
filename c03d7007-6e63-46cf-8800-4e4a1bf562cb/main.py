from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, SMA, BB, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "TSLA", "META"]
        # The data should now be a list of dicts, each containing OHLCV for the tickers

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
            # Iterate through the list of data to extract the relevant OHLCV data for each ticker
            ohlcv = next((entry["ohlcv"] for entry in data if entry["symbol"] == ticker), None)
            
            # Make sure that we have the OHLCV data for the ticker
            if ohlcv is None:
                log(f"No OHLCV data available for {ticker}")
                continue

            # Calculate technical indicators for each ticker
            rsi = RSI(ticker, ohlcv, length=14)
            ema = EMA(ticker, ohlcv, length=20)
            sma = SMA(ticker, ohlcv, length=50)
            bb = BB(ticker, ohlcv, length=20, std=2)  # Standard deviation for BBs
            atr = ATR(ticker, ohlcv, length=14)

            # Log the last values for each indicator to inspect their output
            log(f"{ticker} RSI: {rsi[-1] if rsi else 'N/A'}, EMA: {ema[-1] if ema else 'N/A'}, SMA: {sma[-1] if sma else 'N/A'}, BB Lower: {bb['lower'][-1] if bb else 'N/A'}, BB Upper: {bb['upper'][-1] if bb else 'N/A'}, ATR: {atr[-1] if atr else 'N/A'}")
            
            # Define simple trading logic based on technical indicators
            current_allocation = 0.0  # Default to holding no position
            if rsi and rsi[-1] < 30 and ema[-1] > sma[-1]:  # Basic example criteria for buying
                current_allocation = 1/3  # Equal weight to each ticker for simplicity

            # Update allocation dictionary
            allocation_dict[ticker] = current_allocation

        return TargetAllocation(allocation_dict)