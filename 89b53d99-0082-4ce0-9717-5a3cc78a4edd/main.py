from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, BB, StochasticOscillator as SO, PSAR, OBV
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        # Allocation budget per stock
        self.allocation_per_stock = 1.0 / len(self.tickers)

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        
        for ticker in self.tickers:
            # Calculate indicators
            short_ema = EMA(ticker, data, 9)
            long_ema = EMA(ticker, data, 21)
            rsi = RSI(ticker, data, 14)
            bb = BB(ticker, data, length=20, std=2)
            so = SO(ticker, data)
            psar = PSAR(ticker, data)
            volume = OBV(ticker, data)

            current_price = data["ohlcv"][-1][ticker]["close"]
            average_volume = sum(volume[-20:]) / 20
            current_volume = volume[-1]
            
            buy_signals, sell_signals = 0, 0
            
            # Entry Conditions
            if short_ema[-1] > long_ema[-1]:  # EMA Crossover
                buy_signals += 1
            if rsi[-1] < 30 or (rsi[-2] < 30 and rsi[-1] > rsi[-2]):  # RSI Condition
                buy_signals += 1
            if current_price <= bb["lower"][-1]:  # Touch Lower BB
                buy_signals += 1
            if so[-1]["K"] > so[-1]["D"] and so[-2]["K"] <= so[-2]["D"] and so[-1]["K"] < 20:  # Stochastic Condition
                buy_signals += 1
            if current_volume > 1.5 * average_volume:  # Volume Increase
                buy_signals += 1
            
            # Exit Conditions
            if short_ema[-1] < long_ema[-1]:  # EMA Crossover
                sell_signals += 1
            if rsi[-1] > 70:  # RSI Condition
                sell_signals += 1
            if current_price >= bb["upper"][-1]:  # Touch Upper BB
                sell_signals += 1
            if so[-1]["K"] < so[-1]["D"] and so[-2]["K"] >= so[-2]["D"] and so[-1]["K"] > 80:  # Stochastic Condition
                sell_signals += 1
            if current_price < psar[-1]:  # Price below PSAR
                sell_signals += 1
            # Assuming we have a system to check for a stop-loss condition outside of this if-statement
            
            # Determine allocation based on signals
            if buy_signals >= 3:
                allocation_dict[ticker] = self.allocation_per_stock
            elif sell_signals >= 3 or current_price < psar[-1] * 0.9:  # Including stop-loss condition as part of sell
                allocation_dict[ticker] = 0
            else:
                allocation_dict[ticker] = self.allocation_per_stock if ticker in allocation_dict else 0

        return TargetAllocation(allocation_dict)