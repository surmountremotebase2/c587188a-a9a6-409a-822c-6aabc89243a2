def run(self, data):
    allocation_dict = {ticker: 0 for ticker in self.tickers}

    for ticker in self.tickers:
        ohlcv = data.get("ohlcv", [])
        
        # Check if the 'close' key exists in the ohlcv data
        if not ohlcv:
            logger.error(f"No OHLCV data available for {ticker}")
            continue

        # Log the first few entries of ohlcv for inspection
        logger.info(f"ohlcv data for {ticker}: {ohlcv[:5]}")

        # Ensure 'close' key is in the data and handle accordingly
        close_prices = [entry.get('close', None) for entry in ohlcv]
        if None in close_prices:
            logger.warning(f"Missing 'close' values in OHLCV data for {ticker}. Excluding these entries.")
            close_prices = [price for price in close_prices if price is not None]

        # If there are no valid close prices, skip processing this ticker
        if not close_prices:
            logger.error(f"No valid close prices for {ticker}, skipping.")
            continue

        # The rest of your processing logic (RSI, SMA, MACD, etc.)
        rsi = RSI(ticker, ohlcv, 9)
        short_sma = SMA(ticker, ohlcv, 5)
        long_sma = SMA(ticker, ohlcv, 20)
        macd_line, signal_line = MACD(close_prices, fast_period=9, slow_period=21, signal_period=8)
        bb = BB(ticker, ohlcv, 10, std=2)
        atr = ATR(ticker, ohlcv, 10)
        ema_8 = EMA(ticker, ohlcv, 8)

        # Log values and conditions as before
        logger.info(f"{ticker} - RSI: {rsi[-1]}, Short SMA: {short_sma[-1]}, Long SMA: {long_sma[-1]}")
        logger.info(f"{ticker} - MACD: {macd_line[-1]}, Signal Line: {signal_line[-1]}")
        logger.info(f"{ticker} - Bollinger Bands (Lower): {bb['lower'][-1]}, Upper: {bb['upper'][-1]}")
        logger.info(f"{ticker} - ATR: {atr[-1]}, EMA 8: {ema_8[-1]}")

        # Rest of the conditions and allocation logic...