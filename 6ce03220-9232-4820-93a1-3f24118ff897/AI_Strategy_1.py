from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.asset = "AAPL"
        self.investment = 3000  # Assuming the strategy's basis for money management

    @property
    def assets(self):
        return [self.asset]

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        # Load the OHLCV data for AAPL
        asset_data = data["ohlcv"]
        
        # Ensure there's enough data for EMA calculation
        if len(asset_data) >= 21:  # At least 21 days for EMA21
            # Calculate EMA7 and EMA21 for AAPL
            ema7 = EMA(self.asset, asset_data, 5)[-1]
            ema21 = EMA(self.asset, asset_data, 21)[-1]

            if ema7 > ema21:
                # EMA7 > EMA21, allocate investment to AAPL
                log("EMA7 > EMA21: Buying AAPL")
                # Mock calculation for example; Allocate based on your method
                allocation_ratio = self._calculate_ratio_from_investment(self.investment)
                return TargetAllocation({self.asset: allocation_ratio})
            else:
                # EMA7 < EMA21, liquidate AAPL
                log("EMA7 < EMA21: Selling AAPL")
                return TargetAllocation({self.asset: 0})
        else:
            # Not enough data, do not allocate
            return TargetAllocation({self.asset: 0})

    def _calculate_ratio_from_investment(self, investment):
        """
        Placeholder for a method to convert an investment amount into an allocation ratio.
        The implementation will depend on the account size and other factors.
        
        For simplification in this example, we'll assume a fixed investment using a mock method.
        """
        # This is a mock, replace with actual logic
        return 1  # Implies full investment, enhance with the real method to calculate from $3000

# Note: The actual conversion from a dollar investment ($3000) to an allocation ratio needs real implementation.
# This strategy is simplified for demonstration and assumes full allocation if conditions meet.