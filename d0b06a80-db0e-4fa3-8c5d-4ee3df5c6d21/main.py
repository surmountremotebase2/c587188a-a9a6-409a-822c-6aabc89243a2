from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers we will be trading
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "LMT", "UPS", "WMT", "PEP", "FDX"]
        # Initial allocation of $3000 across the assets, can be adjusted based on strategy requirements
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
            current_rsi = RSI(ticker, data["ohlcv"], length=10)

            # Check if EMA and RSI data are available
            if (current_rsi is not None and len(current_rsi) > 0) and (ema9 is not None and ema21 is not None and len(ema9) > 0 and len(ema21) > 0):
                # Get the most recent RSI value
                latest_rsi = current_rsi[-1]
                if ema9[-1] > ema21[-1] and latest_rsi > 70:
                    # EMA9 > EMA21, RSI>65, fully invest (1)
                    allocation_dict[ticker] = self.initial_investment / len(self.tickers)
                    #log(f"Investing in {ticker}: ${allocation_dict[ticker]:.2f}")
                elif ema9[-1] < ema21[-1] and latest_rsi < 30:
                    # EMA9 < EMA21, RSI < 45, liquidate (0)
                    allocation_dict[ticker] = 0
                    #log(f"Liquidating position for {ticker}")
                else: 
                    # If EMAs are equal, or for any reason not able to decide, hold current position
                    # Not trading signals to hold, assuming it to remain as it is
                    # Maintain the current position if RSI is between 35 and 65
                    # This could be treated as 'no action', or you might want to adjust it based on the strategy's need
                    # Example placeholder for maintaining existing allocation - adjust as necessary
                    # allocation_dict[ticker] = existing_allocation
                    pass
            else:
                # If RSI data is not available, allocate 0 for the ticker
                # If data is not available to compute EMAs, avoid trading
                log(f"Insufficient EMA & RSI data available for {ticker}, no action taken.")
                allocation_dict[ticker] = 0
        # Return the target allocations as a TargetAllocation object
        return TargetAllocation(allocation_dict)