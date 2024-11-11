from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI

class TradingStrategy(Strategy):
    def __init__(self):
        # List of tickers to trade
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "TSLA", "GOOGL", "NFLX"]  # Additional tickers can be added here
        self.initial_investment = 1000  # Initial investment amount
        self.available_funds = self.initial_investment  # Track available funds

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        ohlcv = data.get("ohlcv")
        partial_allocation = 0.3 * (1 / len(self.tickers))  # 0.3 of 1/len(self.tickers)
        
        # Calculate allocation amount per ticker
        per_ticker_investment = self.initial_investment * partial_allocation

        for ticker in self.tickers:
            try:
                # Calculate RSI with a length of 9
                rsi = RSI(ticker, ohlcv, length=9)[-1]

                # Check buy condition: RSI(9) > 65
                if rsi > 70:
                    # Ensure sufficient funds are available before buying
                    if self.available_funds >= per_ticker_investment:
                        allocation_dict[ticker] += partial_allocation
                        # Deduct invested amount from available funds
                        self.available_funds -= per_ticker_investment

                # Check liquidation condition: RSI(9) < 30
                elif rsi < 30:
                    # Liquidate all holdings for the ticker
                    allocation_dict[ticker] = 0
                    # Reset available funds if selling out of positions
                    self.available_funds = self.initial_investment

            except Exception as e:
                # Log any errors for easier debugging
                print(f"Error processing {ticker}: {e}")

        return TargetAllocation(allocation_dict)