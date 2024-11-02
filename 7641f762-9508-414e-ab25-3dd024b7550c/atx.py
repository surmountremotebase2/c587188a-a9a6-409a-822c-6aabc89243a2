#calculate_adx

def calculate_adx(ohlcv, period=14):
    # Calculate the +DI and -DI
    high = ohlcv['high']
    low = ohlcv['low']
    close = ohlcv['close']
    
    # Calculate True Range and Directional Movement
    true_range = high - low
    high_move = high.diff()
    low_move = low.diff()
    
    plus_dm = (high_move.where((high_move > low_move) & (high_move > 0), 0)).rolling(window=period).sum()
    minus_dm = (low_move.where((low_move > high_move) & (low_move > 0), 0)).rolling(window=period).sum()
    
    # Average True Range
    atr = calculate_atr(ohlcv, period)
    
    plus_di = 100 * (plus_dm / atr)
    minus_di = 100 * (minus_dm / atr)

    adx = (abs(plus_di - minus_di) / (plus_di + minus_di)).rolling(window=period).mean() * 100
    return adx