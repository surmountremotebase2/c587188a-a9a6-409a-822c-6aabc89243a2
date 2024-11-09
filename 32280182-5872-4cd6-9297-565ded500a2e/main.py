from datetime import datetime, timedelta
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, MACD, BB, RSI, ADX, ATR, CCI, MFI

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "TSLA"]
        self.holding_dict = {ticker: 0 for ticker in self.tickers}
        self.entry_prices = {ticker: 0 for ticker in self.tickers}
        self.sell_condition_times = {ticker: None for ticker in self.tickers}

    @property
    def interval(self):
        return "1hour"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        ohlcv = data.get("ohlcv")
        current_time = datetime.now()

        for ticker in self.tickers:
            try:
                # Ensure we have valid data for the current ticker
                close_prices = [day[ticker]['close'] for day in ohlcv if ticker in day and 'close' in day[ticker]]
                if len(close_prices) < 13:
                    continue

                # Calculate indicators with close_prices or ticker-specific ohlcv data
                ema9 = EMA(ticker, ohlcv, 9)
                ema21 = EMA(ticker, ohlcv, 21)
                rsi = RSI(ticker, ohlcv, 7)
                macd_line, signal_line = MACD(close_prices, 6, 13, 5)
                bb_data = BB(ticker, ohlcv, 10, 2)
                adx = ADX(ticker, ohlcv, 7)
                atr = ATR(ticker, ohlcv, 7)
                cci = CCI(ticker, ohlcv, 7)
                mfi = MFI(ticker, ohlcv, 7)

                if any(len(x) < 1 for x in [ema9, ema21, rsi, macd_line, signal_line, adx, atr, cci, mfi]):
                    continue

                # Retrieve current indicator values
                current_ema9 = ema9[-1]
                current_ema21 = ema21[-1]
                current_rsi = rsi[-1]
                current_macd = macd_line[-1]
                current_signal = signal_line[-1]
                current_close = close_prices[-1]
                current_bb_lower = bb_data['lower'][-1]
                current_bb_upper = bb_data['upper'][-1]
                current_adx = adx[-1]
                current_atr = atr[-1]
                current_cci = cci[-1]
                current_mfi = mfi[-1]

                # Print indicator values before evaluating conditions
                print(f"\n--- Evaluating Conditions for {ticker} ---")
                print(f"MACD: {current_macd}, Signal Line: {current_signal}")
                print(f"EMA9: {current_ema9}, EMA21: {current_ema21}")
                print(f"RSI: {current_rsi}, ADX: {current_adx}, ATR: {current_atr}, CCI: {current_cci}, MFI: {current_mfi}")
                print(f"BB Lower: {current_bb_lower}, BB Upper: {current_bb_upper}")
                print(f"Close Price: {current_close}")

                # Buy conditions
                buy_conditions_met = sum([
                    current_macd > current_signal and abs(current_ema21 - current_ema9) > 1 and current_rsi > 65 and current_adx > 60 and current_cci > 100 and current_atr > 0.6 and current_mfi < 20,
                    current_close < current_bb_lower and current_rsi < 30 and current_adx > 60 and current_cci < -100
                ])

                if buy_conditions_met >= 1:
                    allocation_dict[ticker] = (3000 / len(self.tickers))
                    self.holding_dict[ticker] += allocation_dict[ticker] / current_close
                    self.entry_prices[ticker] = current_close
                    # Print settings and indicators on Buy
                    print(f"\n--- BUY Signal for {ticker} ---")
                    print(f"Buy Conditions Met:", buy_conditions_met)

                # Sell conditions
                sell_conditions_met = sum([
                    current_signal > current_macd and abs(current_ema21 - current_ema9) > 1 and current_rsi < 35 and current_cci < -100 and current_atr > 0.6 and current_adx > 60,
                    current_close > current_bb_upper and current_rsi > 70 and (current_atr > 0.7 and current_adx > 70) and (current_atr > 0.75 or current_adx > 75) and current_cci > 100
                ])

                if sell_conditions_met >= 1:
                    if self.sell_condition_times[ticker] is None:
                        self.sell_condition_times[ticker] = current_time
                    elif current_time >= self.sell_condition_times[ticker] + timedelta(minutes=5):
                        allocation_dict[ticker] = 0
                        self.holding_dict[ticker] = 0
                        self.sell_condition_times[ticker] = None
                        # Print settings and indicators on Sell
                        print(f"\n--- SELL Signal for {ticker} ---")
                        print(f"Sell Conditions Met:", sell_conditions_met)
                else:
                    self.sell_condition_times[ticker] = None

                # Stop-loss condition based on ATR and ADX
                if self.holding_dict[ticker] > 0:
                    stop_loss_price = self.entry_prices[ticker] - (1.0 * current_atr)
                    if current_close < stop_loss_price and current_adx > 25:
                        allocation_dict[ticker] = 0
                        self.holding_dict[ticker] = 0
                        print(f"\n--- STOP-LOSS Triggered for {ticker} ---")
                        print(f"Stop-loss Price: {stop_loss_price}, Current Price: {current_close}")
                        print(f"Entry Price: {self.entry_prices[ticker]}, ATR: {current_atr}, ADX: {current_adx}")

            except TypeError as e:
                print(f"Data error for {ticker}: {e}")
                pass  # Placeholder for the except block

        return TargetAllocation(allocation_dict)