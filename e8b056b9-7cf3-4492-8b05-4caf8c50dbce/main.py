from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Tickers to trade
        self.tickers = ["AAPL"]
        
        # Initializing an empty data list since MACD calculations are handled internally
        self.data_list = []
        
    @property
    def interval(self):
        # Set interval for MACD indicator calculation
        return "1day"
    
    @property
    def assets(self):
        # Return the list of tickers this strategy trades
        return self.tickers
    
    @property
    def data(self):
        # Return the data list (empty, as data needed for MACD calculation is fetched internally)
        return self.data_list
    
    def run(self, data):
        # Initialize allocation dictionary with no allocation
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        
        for ticker in self.tickers:
            # Calculate MACD for the ticker
            macd = MACD(ticker, data["ohlcv"], fast=12, slow=26, signal=9)
            
            # macd[‘MACD’] and macd[‘signal’] are lists of MACD values and signal line values, respectively.
            # We check the last two values to determine a crossover.
            if len(macd['MACD']) >= 2 and len(macd['signal']) >= 2:
                macd_current = macd['MACD'][-1]
                macd_previous = macd['MACD'][-2]
                signal_current = macd['signal'][-1]
                signal_previous = macd['signal'][-2]
                
                # Check for crossover
                # Buy signal: MACD crosses above signal line
                if macd_previous < signal_previous and macd_current > signal_current:
                    log(f"Buying {ticker}")
                    allocation_dict[ticker] = 1  # Allocate 100% to the ticker
                    
                # Sell signal: MACD crosses below signal line
                elif macd_previous > signal_previous and macd_current < signal_current:
                    log(f"Selling {ticker}")
                    allocation_dict[ticker] = 0  # Allocate 0% to the ticker (could also sell if short selling is allowed)
                    
                # No clear signal, do nothing
                else:
                    log(f"No clear signal for {ticker}")
        
        # Return the calculated target allocation based on MACD signals
        return TargetAllocation(allocation_dict)