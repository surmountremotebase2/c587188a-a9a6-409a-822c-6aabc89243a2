# calculate_atr.py

def calculate_atr(ohlcv, period=14):
    # ohlcv is expected to be a DataFrame with columns: ['high', 'low', 'close']
    high_low = ohlcv['high'] - ohlcv['low']
    high_prev_close = abs(ohlcv['high'] - ohlcv['close'].shift(1))
    low_prev_close = abs(ohlcv['low'] - ohlcv['close'].shift(1))

    true_range = pd.DataFrame({
        'high_low': high_low,
        'high_prev_close': high_prev_close,
        'low_prev_close': low_prev_close
    }).max(axis=1)

    atr = true_range.rolling(window=period).mean()
    return atr