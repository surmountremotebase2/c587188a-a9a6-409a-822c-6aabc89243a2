from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, SMA, BB, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "TSLA", "META"]
        # The data should now be a list of dicts or something structured correctly

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}

        # Log the data structure for debugging purposes
        log(f"Data structure: {data}")
        
        for ticker in self.tickers:
            # Ensure that data is in the expected format and access it accordingly
            for entry in data:
                # Log the entry to check its type
                log(f"Processing entry: {entry}")

                if isinstance(entry, dict) and "symbol" in entry:
                    # Extract OHLCV data if entry is a dictionary
                    if entry["symbol"] == ticker:
                        ohlcv = entry.get("ohlcv", [])
                        
                        # Make sure we have OHLCV data
                        if not ohlcv:
                            log(f"No OHLCV data available for {ticker}")
                            continue
                        
                        # Calculate technical indicators
                        rsi = RSI(ticker, ohlcv, length=14)
                        ema = EMA(ticker, ohlcv, length=20)
                        sma = SMA(ticker, ohlcv, length=50)
                        bb = BB(ticker, ohlcv, length=20, std=2)
                        atr = ATR(ticker, ohlcv, length=14)
                        
                        # Log indicator values for debugging
                        log(f"{ticker} RSI: {rsi[-1] if rsi else 'N/A'}, EMA: {ema[-1] if ema else 'N/A'}, SMA: {sma[-1] if sma else 'N/A'}, BB Lower: {bb['lower'][-1] if bb else 'N/A'}, BB Upper: {bb['upper'][-1] if bb else 'N/A'}, ATR: {atr[-1] if atr else 'N/A'}")
                        
                        # Define allocation based on indicators
                        current_allocation = 0.0
                        if rsi and rsi[-1] < 30 and ema[-1] > sma[-1]:  # Example condition
                            current_allocation = 1/3  # Allocate 1/3 to the ticker

                        # Update allocation dictionary
                        allocation_dict[ticker] = current_allocation
                        
                        break  # Found the ticker, no need to continue checking other entries

        return TargetAllocation(allocation_dict)