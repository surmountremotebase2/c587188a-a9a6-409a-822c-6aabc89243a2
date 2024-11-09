import logging
from .macd import MACD  # Import the custom MACD function
from surmount.technical_indicators import RSI, SMA, EMA, BB, ATR
from surmount.base_class import Strategy, TargetAllocation

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingStrategy(Strategy):
    def __init__(self):
        # Define assets and data
        self.tickers = ["AAPL", "NVDA", "GOOGL", "AMZN"]
        self.data_list = []  # Populate with required data if needed
    
    @property
    def interval(self):
        return "1hour"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}

        for ticker in self.tickers:
            # Get OHLCV data for the ticker
            ohlcv = data.get("ohlcv")
            close_prices = [entry["close"] for entry in ohlcv]

            # Calculate indicators
            rsi = RSI(ticker, ohlcv, 9)
            short_sma = SMA(ticker, ohlcv, 5)
            long_sma = SMA(ticker, ohlcv, 20)
            macd_line, signal_line = MACD(close_prices, fast_period=9, slow_period=21, signal_period=8)
            bb = BB(ticker, ohlcv, 10, std=2)
            atr = ATR(ticker, ohlcv, 10)
            ema_8 = EMA(ticker, ohlcv, 8)  # 8-period EMA

            # Log the calculated values for debugging
            logger.info(f"{ticker} - RSI: {rsi[-1]}, Short SMA: {short_sma[-1]}, Long SMA: {long_sma[-1]}")
            logger.info(f"{ticker} - MACD: {macd_line[-1]}, Signal Line: {signal_line[-1]}")
            logger.info(f"{ticker} - Bollinger Bands (Lower): {bb['lower'][-1]}, Upper: {bb['upper'][-1]}")
            logger.info(f"{ticker} - ATR: {atr[-1]}, EMA 8: {ema_8[-1]}")
            
            # Define buy/sell conditions
            buy_conditions = [
                rsi[-1] > 55,
                short_sma[-1] > long_sma[-1],
                macd_line[-1] > signal_line[-1],
                ohlcv[-1]["close"] < bb["lower"][-1] and rsi[-1] < 40,
                close_prices[-1] > ema_8[-1]  # EMA condition for buy
            ]

            sell_conditions = [
                long_sma[-1] > short_sma[-1] and rsi[-1] < 45,
                signal_line[-1] > macd_line[-1],
                ohlcv[-1]["close"] > bb["upper"][-1] and rsi[-1] > 60,
                rsi[-1] < 45,
                close_prices[-1] < ema_8[-1]  # EMA condition for sell
            ]

            # Log the conditions being checked
            logger.info(f"Checking conditions for {ticker}:")
            logger.info(f"Buy conditions: {buy_conditions}")
            logger.info(f"Sell conditions: {sell_conditions}")

            # Allocate if buy conditions are met
            if sum(buy_conditions) >= 3:
                allocation_dict[ticker] = 1 / len(self.tickers)  # Equal allocation
                logger.info(f"Buying {ticker} - Conditions met: {buy_conditions}")

            # Deallocate if sell conditions are met
            if sum(sell_conditions) >= 3:
                allocation_dict[ticker] = 0  # Exit position
                logger.info(f"Selling {ticker} - Conditions met: {sell_conditions}")

        return TargetAllocation(allocation_dict)