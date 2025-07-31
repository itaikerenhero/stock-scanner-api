from scanner.technicals import calculate_technicals, is_valid_setup, describe_setup

def filter_stocks(stock_data_dict):
    """
    Filter all stocks in the dictionary and return only valid setups.
    """
    setups = []

    for ticker, df in stock_data_dict.items():
        try:
            df = calculate_technicals(df)
            if is_valid_setup(df):
                setup_type = describe_setup(df)
                setups.append({
                    "ticker": ticker,
                    "setup": setup_type,
                    "price": df["Close"].iloc[-1],
                    "rsi": df["RSI"].iloc[-1],
                    "sma_20": df["SMA_20"].iloc[-1],
                    "sma_50": df["SMA_50"].iloc[-1],
                })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    return setups
