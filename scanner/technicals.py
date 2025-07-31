import pandas as pd
import pandas_ta as ta

def calculate_technicals(df):
    if df is None or df.empty:
        raise ValueError("DataFrame is empty or None.")

    required_cols = ['Close', 'High', 'Low', 'Open', 'Volume']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df = df.copy()

    # Bail out early if not enough data
    if len(df) < 30:
        return pd.DataFrame()

    # Indicators
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['SMA_50'] = ta.sma(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['20d_high'] = df['High'].rolling(window=20).max()
    df['Avg_Volume_20'] = df['Volume'].rolling(window=20).mean()

    # Shifted versions to avoid shape mismatch
    df['prev_close'] = df['Close'].shift(1)
    df['prev_high'] = df['High'].shift(1)
    df['prev_low'] = df['Low'].shift(1)
    df['prev_sma20'] = df['SMA_20'].shift(1)
    df['prev_20d_high'] = df['20d_high'].shift(1)

    # Drop all NaNs created by indicators and shifts
    df.dropna(inplace=True)

    # Signal flags (safe)
    df['Breakout'] = df['Close'] > df['prev_20d_high']
    df['Pullback_Bounce'] = (
        (df['Close'] > df['SMA_50']) &
        (df['prev_low'] < df['prev_sma20']) &
        (df['Close'] > df['prev_close'])
    )

    # New bullish criteria
    df['Volume_Spike'] = df['Volume'] > df['Avg_Volume_20'] * 1.5
    df['Big_Green'] = (df['Close'] > df['Open']) & (df['Close'] > df['prev_high'])
    df['RSI_Strength'] = df['RSI'] > 55
    df['Above_SMA20'] = df['Close'] > df['SMA_20']

    df['Bullish_Momentum'] = (
        df['Volume_Spike'] &
        df['Big_Green'] &
        df['RSI_Strength'] &
        df['Above_SMA20']
    )

    return df


def is_valid_setup(df):
    if df is None or df.empty or len(df) < 30:
        return False

    latest = df.iloc[-1]
    return bool(
        latest.get('Breakout', False) or
        latest.get('Pullback_Bounce', False) or
        latest.get('Bullish_Momentum', False)
    )


def describe_setup(df):
    latest = df.iloc[-1]
    if latest.get('Breakout', False):
        return "Breakout setup"
    elif latest.get('Pullback_Bounce', False):
        return "Pullback & bounce setup"
    elif latest.get('Bullish_Momentum', False):
        return "Bullish momentum setup"
    else:
        return "No clear setup"
