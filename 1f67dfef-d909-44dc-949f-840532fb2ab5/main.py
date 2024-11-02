from surmount.technical_indicators import MACD

# Example OHLCV data for AAPL
# You should replace this with your actual data source
data = {
    "ohlcv": {
        "AAPL": [
            {"close": 150, "open": 145, "high": 155, "low": 144},
            {"close": 152, "open": 150, "high": 158, "low": 149},
            {"close": 155, "open": 152, "high": 160, "low": 150},
            # Add more OHLCV data as needed
        ]
    }
}

# Calculate MACD for AAPL
macd_data = MACD("AAPL", data["ohlcv"]["AAPL"], fast=12, slow=26)

# Print the MACD data and its structure
print("MACD Data for AAPL:")
print(macd_data)

# Print the data structure
print("\nData Structure for AAPL OHLCV:")
print(data["ohlcv"]["AAPL"])