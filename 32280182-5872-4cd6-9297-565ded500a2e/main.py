from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, MACD, BB, RSI, ADX, ATR, CCI, MFI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]
        self.holdings = {ticker: 0 for ticker in self.tickers}
        self.entry_prices = {ticker: 0 for ticker in self.tickers}
    
    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        allocation = {ticker: 0.0 for ticker in self.tickers}

        for ticker in self.tickers:
            # Ensure data contains sufficient entries
            if len(data["ohlcv"]) < 26:
                continue

            # Prepare close prices as a list of recent values for the ticker
            close_prices = [entry[ticker]["close"] for entry in data["ohlcv"] if ticker in entry]

            # Calculate indicators
            ema9 = EMA(ticker, data["ohlcv"], 9)
            ema21 = EMA(ticker, data["ohlcv"], 21)
            macd_result = MACD(close_prices, 12, 26, 9) if len(close_prices) >= 26 else (None, None)
            macd_line, signal_line = macd_result
            bb_data = BB(ticker, data["ohlcv"], 20, 2)
            rsi = RSI(ticker, data["ohlcv"], 14)
            adx = ADX(ticker, data["ohlcv"], 14)
            atr = ATR(ticker, data["ohlcv"], 14)
            cci = CCI(ticker, data["ohlcv"], 14)
            mfi = MFI(ticker, data["ohlcv"], 14)
            
            # Get the latest indicator values and price
            last_close = data["ohlcv"][-1][ticker]["close"]
            last_ema9 = ema9[-1] if ema9 else None
            last_ema21 = ema21[-1] if ema21 else None
            last_macd = macd_line[-1] if macd_line else None
            last_signal = signal_line[-1] if signal_line else None
            last_bb_lower = bb_data['lower'][-1] if 'lower' in bb_data else None
            last_bb_upper = bb_data['upper'][-1] if 'upper' in bb_data else None
            last_rsi = rsi[-1] if rsi else None
            last_adx = adx[-1] if adx else None
            last_atr = atr[-1] if atr else None
            last_cci = cci[-1] if cci else None
            last_mfi = mfi[-1] if mfi else None

            # Log values for debugging
            log(f"\nEvaluating {ticker}: Close={last_close}, EMA9={last_ema9}, EMA21={last_ema21}, "
                f"MACD={last_macd}, Signal={last_signal}, BB Lower={last_bb_lower}, BB Upper={last_bb_upper}, "
                f"RSI={last_rsi}, ADX={last_adx}, ATR={last_atr}, CCI={last_cci}, MFI={last_mfi}")

            # Buy Condition
            buy_condition = (
                (last_macd > last_signal) and 
                (abs(last_ema21 - last_ema9) > 1) and 
                ((last_rsi > 65) or (last_mfi < 20)) and 
                (last_adx > 60) and 
                (last_cci > 100) and 
                (last_atr > 0.6) and 
                (last_mfi < 20)
            )
            
            secondary_buy_condition = (
                (last_close < last_bb_lower) and 
                (last_rsi < 30) and 
                (last_adx > 60) and 
                (last_cci < -100)
            )
            
            # Sell Condition
            sell_condition = (
                (last_signal > last_macd) and 
                (abs(last_ema21 - last_ema9) > 1) and 
                ((last_rsi < 35) or (last_mfi > 80)) and 
                (last_cci < -100) and 
                (last_atr > 0.6) and 
                (last_adx > 60)
            )
            
            secondary_sell_condition = (
                (last_close > last_bb_upper) and 
                (last_rsi > 70) and 
                ((last_atr > 0.7 and last_adx > 70) or (last_atr > 0.75 or last_adx > 75)) and 
                (last_cci > 100)
            )

            # Execute Buy Action if Conditions are Met
            if buy_condition or secondary_buy_condition:
                allocation[ticker] = 1.0  # Allocating full capital to this stock
                self.holdings[ticker] = allocation[ticker] / last_close
                self.entry_prices[ticker] = last_close
                log(f"\n--- BUY {ticker} ---\n"
                    f"Condition Met: {'Primary' if buy_condition else 'Secondary'}\n"
                    f"Settings: Close={last_close}, ATR={last_atr}, ADX={last_adx}")

            # Execute Sell Action if Conditions are Met
            elif sell_condition or secondary_sell_condition:
                allocation[ticker] = 0.0  # Sell entire holding
                self.holdings[ticker] = 0.0
                log(f"\n--- SELL {ticker} ---\n"
                    f"Condition Met: {'Primary' if sell_condition else 'Secondary'}\n"
                    f"Settings: Close={last_close}, ATR={last_atr}, ADX={last_adx}")

            # Stop-loss Condition (optional)
            if self.holdings[ticker] > 0:
                stop_loss_price = self.entry_prices[ticker] - last_atr
                if last_close < stop_loss_price and last_adx > 25:
                    allocation[ticker] = 0.0
                    self.holdings[ticker] = 0.0
                    log(f"\n--- STOP-LOSS {ticker} ---\n"
                        f"Triggered: Close={last_close} below Stop-loss={stop_loss_price}")

        return TargetAllocation(allocation)