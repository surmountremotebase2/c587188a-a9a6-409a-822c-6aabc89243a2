from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, MACD, BB
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "AMD", "META"]
        # Each stock gets an equal part of the $3000, meaning each gets $500.
        # However, for allocation, we work with proportion (0 to 1), not direct dollar amounts.
        self.equal_allocation = 1 / len(self.tickers)  

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"  # Choose appropriate interval based on strategy needs

    def run(self, data):
        allocation = {}
        for ticker in self.assets:
            # Extracting indicators
            macd_signal = MACD(ticker, data, 12, 26)['signal'][-1]
            macd_line = MACD(ticker, data, 12, 26)['MACD'][-1]
            rsi = RSI(ticker, data, 14)[-1]
            ema_short = EMA(ticker, data, 9)[-1]
            ema_long = EMA(ticker, data, 21)[-1]
            bb = BB(ticker, data, 20, 2)
            
            # Defining buy and sell signals
            buy_signals = 0
            sell_signals = 0
            
            # MACD buy/sell signal
            if macd_line > macd_signal:
                buy_signals += 1
            else:
                sell_signals += 1

            # RSI buy/sell signal
            if rsi < 30:
                buy_signals += 1
            elif rsi > 70:
                sell_signals += 1

            # EMA crossover buy/sell signal
            if ema_short > ema_long:
                buy_signals += 1
            elif ema_short < ema_long:
                sell_signals += 1
            
            # Bollinger Bands stop-loss logic (simplified)
            if data[-1][ticker]['close'] < bb['lower'][-1]:  # Assuming entry price is close to current price
                log(f"{ticker}: Stop-loss triggered.")
                sell_signals += 1

            # Decision making based on buy and sell signals
            if buy_signals >= 3 and sell_signals < 2:
                # Allocate equally if 3 indicators show upward trend and stop-loss not hit
                allocation[ticker] = self.equal_allocation
            else:
                # No allocation if conditions are not met
                allocation[ticker] = 0

        return TargetAllocation(allocation)