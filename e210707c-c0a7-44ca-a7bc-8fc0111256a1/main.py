from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import BB
from surmount.logging import log
from surmount.constants import TRANSACTION_TYPE_BUY, TRANSACTION_TYPE_SELL

class TradingStrategy(Strategy):
    def __init__(self):
        # Initialize with the ticker of interest
        self.ticker = "AAPL"  # Example asset ticker
        self.bb_length = 20  # 20 periods for Bollinger Bands
        self.bb_std = 2  # Standard deviation multiplier for Bollinger Bands
        self.initial_investment = 3000  # Total funds to invest
        self.investment_per_asset = 3000  # Assuming a single asset for simplicity

    @property
    def assets(self):
        # Define the asset to trade
        return [self.ticker]

    @property
    def interval(self):
        # Data interval for indicators and strategy decision making
        return "1day"

    def run(self, data):
        # Retrieve Bollinger Bands for the ticker
        bb_bands = BB(self.ticker, data["ohlcv"], self.bb_length, self.bb_std)
        
        # Check if Bollinger Bands data is available
        if bb_bands is None or len(bb_bands['lower']) == 0:
            log("Bollinger Bands data not available for the decision-making process.")
            return TargetAllocation({self.ticker: 0})
        
        # Current asset price (latest close price)
        current_price = data["ohlcv"][-1][self.ticker]['close']
        
        # Decide on allocation based on the relationship of the price to the Bollinger Bands
        if current_price <= bb_bands['lower'][-1]:
            # Price touches or falls below the lower Bollinger Band - Buy signal
            log(f"Price touches or below the lower BB, considering buying {self.ticker}.")
            allocation = {self.ticker: 1}  # Assumes full investment in the selected asset
        elif current_price >= bb_bands['upper'][-1]:
            # Price touches or exceeds the upper Bollinger Band - Sell signal
            log(f"Price touches or exceeds the upper BB, considering selling {self.ticker}.")
            allocation = {self.ticker: 0}  # Liquidates the position
        else:
            # No action if the price is within the Bollinger Bands
            log("Price is within Bollinger Bands, no action taken.")
            # Maintain current allocation, this assumes you can fetch current allocation. Placeholder value here.
            current_allocation = 0  # Placeholder, fetch actual current allocation if available
            allocation = {self.ticker: current_allocation}

        return TargetAllocation(allocation)