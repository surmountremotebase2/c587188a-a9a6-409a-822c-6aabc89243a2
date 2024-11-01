#Type code here
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers we will be trading
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        # Initial allocation of $3000 across the assets
        self.initial_investment = 3000

    @property
    def assets(self):
        # Return the list of tickers this strategy will handle
        return self.tickers

    @property
    def interval(self):
        # Set the interval to 1-hour for both EMA and RSI calculations
        return "1hour"

    def run(self, data):
        """
        Execute the trading strategy based on both EMA and RSI conditions.
        
        :param data: The data context provided by the Surmount framework.
        :return: Returns a TargetAllocation object with the target allocations.
        """
        # Initialize the allocation dictionary
        allocation_dict = {}

        # Iterate over each ticker to calculate its EMA and RSI
        for ticker in self.tickers:
            # Calculate EMA9 and EMA21 for the current ticker
            ema9 = EMA(ticker, data, 9)
            ema21 = EMA(ticker, data, 21)

            # Calculate the RSI for the current ticker
            current_rsi = RSI(ticker, data["ohlcv"], length=4)

            # Check if EMA data is available
            if ema9 is not None and ema21 is not None and len(ema9) > 0 and len(ema21) > 0:
                # Compare the last available EMA values
                if ema9[-1] > ema21[-1]:
                    allocation_dict[ticker] = self.initial_investment / len(self.tickers)  # Invest fully
                elif ema9[-1] < ema21[-1]:
                    allocation_dict[ticker] = 0  # Liquidate position
                else:
                    log(f"No clear EMA crossover signal for {ticker}")

            # Check if RSI data is available
            if current_rsi is not None and len(current_rsi) > 0:
                latest_rsi = current_rsi[-1]

                # Adjust allocation based on RSI conditions
                if latest_rsi < 35:
                    allocation_dict[ticker] = self.initial_investment / len(self.tickers)
                elif latest_rsi > 65:
                    allocation_dict[ticker] = 0
                else:
                    # Maintain current position based on RSI
                    allocation_dict[ticker] = allocation_dict.get(ticker, 0)  # Keep existing allocation or 0 if not set
            else:
                allocation_dict[ticker] = 0  # Default to not investing if no RSI data

        # Return the target allocations as a TargetAllocation object
        return TargetAllocation(allocation_dict)