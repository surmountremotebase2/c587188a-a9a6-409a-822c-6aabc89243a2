from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers we will be trading
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        # Initial allocation of $3000 across the assets, can be adjusted based on strategy requirements
        self.initial_investment = 3000

    @property
    def assets(self):
        # Return the list of tickers this strategy will handle
        return self.tickers

    @property
    def interval(self):
        # Set the interval to 1-hour for RSI calculation
        return "1hour"

    def run(self, data):
        """
        Execute the trading strategy based on RSI conditions.
        
        :param data: The data context provided by the Surmount framework.
        :return: Returns a TargetAllocation object with the target allocations.
        """
        # Initialize the allocation dictionary
        allocation_dict = {}

        # Iterate over each ticker to calculate its RSI and determine its target allocation
        for ticker in self.tickers:
            # Calculate the RSI for the current ticker
            current_rsi = RSI(ticker, data["ohlcv"], length=4)
            
            # Check if the RSI data is available
            if current_rsi is not None and len(current_rsi) > 0:
                # Get the most recent RSI value
                latest_rsi = current_rsi[-1]

                # If RSI drops below 35, invest in the stock
                if latest_rsi < 35:
                    allocation_dict[ticker] = self.initial_investment / len(self.tickers)
                # If RSI goes above 65, liquidate the position
                elif latest_rsi > 65:
                    allocation_dict[ticker] = 0
                else:
                    # Maintain the current position if RSI is between 35 and 65
                    # This could be treated as 'no action', or you might want to adjust it based on the strategy's need
                    # Example placeholder for maintaining existing allocation - adjust as necessary
                    # allocation_dict[ticker] = existing_allocation
                    pass
            else:
                # If RSI data is not available, allocate 0 for the ticker
                allocation_dict[ticker] = 0

        # Return the target allocations as a TargetAllocation object
        return TargetAllocation(allocation_dict)