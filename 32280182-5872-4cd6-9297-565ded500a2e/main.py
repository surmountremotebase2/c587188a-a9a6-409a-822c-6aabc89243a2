# main.py
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, MACD, ADX, ATR, CCI, BollingerBands, RSI, MFI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers of interest
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]
        self.initial_investment = 2000
        self.invested_amount = 0
        self.positions = {ticker: {"amount": 0.0, "entry_price": 0.0, "stop_loss": 0.0} for ticker in self.tickers}

    @property
    def assets(self):
        # Return all tickers
        return self.tickers

    @property
    def interval(self):
        # Set 1-hour interval
        return "1hour"

    def run(self, data):
        allocation = {ticker: 0.0 for ticker in self.tickers}

        for ticker in self.tickers:
            ohlcv = data["ohlcv"][ticker]
            if len(ohlcv) < 26:  # Ensure minimum data length for indicators
                continue

            # Calculate indicators
            ema9 = EMA(ticker, ohlcv, length=9)
            ema21 = EMA(ticker, ohlcv, length=21)
            macd, signal = MACD(ticker, ohlcv, 12, 26, 9)
            adx = ADX(ticker, ohlcv, 14)
            atr = ATR(ticker, ohlcv, 14)
            cci = CCI(ticker, ohlcv, 14)
            bb = BollingerBands(ticker, ohlcv, 20, 2)
            rsi = RSI(ticker, ohlcv, 14)
            mfi = MFI(ticker, ohlcv, 14)

            # Fetch latest values
            last_price = ohlcv[-1]["close"]
            last_ema9 = ema9[-1]
            last_ema21 = ema21[-1]
            last_macd = macd[-1]
            last_signal = signal[-1]
            last_adx = adx[-1]
            last_atr = atr[-1]
            last_cci = cci[-1]
            last_bb_lower = bb["lower"][-1]
            last_bb_upper = bb["upper"][-1]
            last_rsi = rsi[-1]
            last_mfi = mfi[-1]

            # Determine buy condition
            buy_condition = (
                (last_macd > last_signal and last_ema21 > last_ema9 and (last_rsi > 65 or last_mfi < 20) and last_adx > 60 and last_cci > 100 and last_atr > 0.6 and last_mfi < 20)
                or (last_price < last_bb_lower and last_rsi < 30 and last_adx > 60 and last_cci < -100)
            )

            # Determine sell condition
            sell_condition = (
                (last_signal > last_macd and last_ema9 > last_ema21 and (last_rsi < 35 or last_mfi > 80) and last_cci < -100 and last_atr > 0.6 and last_adx > 60)
                or (last_price > last_bb_upper and last_rsi > 70 and (last_atr > 0.7 and last_adx > 70) and (last_atr > 0.75 or last_adx > 75) and last_cci > 100)
            )

            # Check for existing positions and apply stop loss
            if self.positions[ticker]["amount"] > 0:
                entry_price = self.positions[ticker]["entry_price"]
                stop_loss = self.positions[ticker]["stop_loss"]
                # If price hits the stop loss, sell the position
                if last_price <= stop_loss:
                    allocation[ticker] = 0.0  # Sell all holdings
                    self.invested_amount -= self.positions[ticker]["amount"] * entry_price
                    self.positions[ticker] = {"amount": 0.0, "entry_price": 0.0, "stop_loss": 0.0}
                    log(f"Stop Loss Triggered for {ticker}: Current Price {last_price}, Stop Loss {stop_loss}, Liquidating position.")

            # Implement buying or selling based on conditions
            if buy_condition and self.positions[ticker]["amount"] == 0.0:  # Only buy if not holding
                available_funds = self.initial_investment - self.invested_amount
                proportion = 1 / len(self.tickers)
                investment_per_stock = available_funds * proportion
                allocation[ticker] = min(1.0, investment_per_stock / last_price)
                self.invested_amount += investment_per_stock

                # Set the stop loss based on ATR
                stop_loss = last_price - (2 * last_atr)  # Example: stop loss at 2x ATR below entry price
                self.positions[ticker] = {"amount": allocation[ticker], "entry_price": last_price, "stop_loss": stop_loss}

                log(f"Buying {ticker}: Current Price {last_price}, Allocation {allocation[ticker]}, Stop Loss {stop_loss}")

            elif sell_condition and self.positions[ticker]["amount"] > 0.0:  # Only sell if holding
                allocation[ticker] = 0.0  # Sell all holdings
                self.invested_amount -= self.positions[ticker]["amount"] * last_price
                self.positions[ticker] = {"amount": 0.0, "entry_price": 0.0, "stop_loss": 0.0}
                log(f"Selling {ticker}: Current Price {last_price}, Liquidating all holdings.")

        return TargetAllocation(allocation)