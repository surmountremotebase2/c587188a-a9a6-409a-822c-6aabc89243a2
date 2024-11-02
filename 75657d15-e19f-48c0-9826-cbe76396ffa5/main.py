from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, SMA, BB, SO, ATR, PSAR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        # Equal allocation according to the funds available and number of stocks
        self.allocation_per_stock = 1 / len(self.tickers)  
        
    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"  # Using daily intervals for this strategy

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            indicators = self.calculate_indicators(ticker, data["ohlcv"])
            # Decision making based on indicators for each stock
            if self.enter_position(indicators):
                allocation_dict[ticker] = self.allocation_per_stock
            elif self.exit_position(indicators):
                allocation_dict[ticker] = 0
            else:
                # Maintain current allocation if neither entry nor exit condition is met
                current_allocation = self.current_allocation(ticker)
                allocation_dict[ticker] = current_allocation
        
        return TargetAllocation(allocation_dict)

    def calculate_indicators(self, ticker, ohlcv_data):
        # Implementation of technical indicators for a given ticker
        rsi = RSI(ticker, ohlcv_data, length=14)
        sma_short = SMA(ticker, ohlcv_data, length=50)
        sma_long = SMA(ticker, ohlcv_data, length=200)
        bb = BB(ticker, ohlcv_data, length=20, std=2)
        so = SO(ticker, ohlcv_data)
        atr = ATR(ticker, ohlcv_data, length=14)
        psar = PSAR(ticker, ohlcv_data)
        # Collect all indicators in a dictionary for easy access
        indicators = {
            "RSI": rsi[-1] if rsi else None,
            "SMA_SHORT": sma_short[-1] if sma_short else None,
            "SMA_LONG": sma_long[-1] if sma_long else None,
            "BB_UPPER": bb["upper"][-1] if bb else None,
            "BB_LOWER": bb["lower"][-1] if bb else None,
            "SO": so[-1] if so else None,
            "ATR": atr[-1] if atr else None,
            "PSAR": psar[-1] if psar else None
        }
        return indicators

    def enter_position(self, indicators):
        # Define conditions to enter a trade
        if indicators["RSI"] < 30 and indicators["SMA_SHORT"] > indicators["SMA_LONG"]:
            return True
        elif indicators["SO"] < 20:
            return True
        # Additional entry conditions can be defined here
        return False

    def exit_position(self, indicators):
        # Define conditions to exit a trade (including the stop-loss logic)
        if indicators["RSI"] > 70:
            return True
        elif indicators["SMA_SHORT"] < indicators["SMA_LONG"]:
            return True
        # Additional exit conditions can be defined here
        # Note: The stop-loss logic typically requires tracking the entry price and comparing it with the current price against the stop-loss threshold. This functionality would need a mechanism to store and access trade history or account for price movement within the strategy, which is not directly depicted in this example.
        return False

    def current_allocation(self, ticker):
        # This method should return the current allocation for a ticker, which involves accessing the strategy's state or holdings. As a placeholder, let's assume an equal allocation without considering dynamic changes.
        # Implement actual logic to fetch current allocation based on strategy's position and portfolio state
        return self.allocation_per_stock