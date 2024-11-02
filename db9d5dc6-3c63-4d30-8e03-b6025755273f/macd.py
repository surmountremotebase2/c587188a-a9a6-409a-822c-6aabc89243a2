# macd.py
import pandas as pd

def MACD(close_prices, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate the MACD line and signal line.

    Parameters:
    close_prices (List[float]): List of closing prices.
    fast_period (int): The period for the fast EMA.
    slow_period (int): The period for the slow EMA.
    signal_period (int): The period for the signal line (EMA of the MACD line).

    Returns:
    Tuple[List[float], List[float]]: A tuple containing the MACD line and the signal line.
    """
    prices_df = pd.DataFrame(close_prices, columns=['close'])

    # Calculate the fast and slow EMAs
    prices_df['EMA_fast'] = prices_df['close'].ewm(span=fast_period, adjust=False).mean()
    prices_df['EMA_slow'] = prices_df['close'].ewm(span=slow_period, adjust=False).mean()

    # Calculate the MACD line
    prices_df['MACD'] = prices_df['EMA_fast'] - prices_df['EMA_slow']

    # Calculate the signal line (EMA of MACD line)
    prices_df['Signal_Line'] = prices_df['MACD'].ewm(span=signal_period, adjust=False).mean()

    # Extract MACD and Signal Line as lists
    macd_line = prices_df['MACD'].tolist()
    signal_line = prices_df['Signal_Line'].tolist()

    return macd_line, signal_line