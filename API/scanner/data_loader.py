import pandas as pd
import yfinance as yf
import requests
import re

def get_data(ticker, period="6mo", interval="1d"):
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df.columns.name = None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    required = ["Close", "High", "Low"]
    if not all(col in df.columns for col in required):
        raise ValueError(f"Missing columns: {required}")

    return df

def parse_price(price_str):
    try:
        if not price_str or price_str == "N/A":
            return None
        return float(re.sub(r"[^\d.]", "", price_str))
    except:
        return None

def get_all_screener_data():
    exchanges = ["nasdaq", "nyse", "amex"]
    all_rows = []

    for ex in exchanges:
        print(f"🌐 Fetching from {ex.upper()}...")
        url = f"https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=5000&exchange={ex}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()
            rows = data["data"]["table"]["rows"]
            all_rows.extend(rows)
        except Exception as e:
            print(f"⚠️ Failed to fetch from {ex.upper()}: {e}")

    return pd.DataFrame(all_rows)

def get_tickers(price_filter="all", limit=500):
    """
    Loads tickers from NASDAQ, NYSE, and AMEX.
    Filters by price using screener's 'lastsale' field.
    """
    try:
        df = get_all_screener_data()
        df = df.rename(columns={"symbol": "Symbol", "lastsale": "LastSale"})
        df["Price"] = df["LastSale"].apply(parse_price)
        df = df[["Symbol", "Price"]].dropna()
        df = df[df["Price"] > 0]

        # Apply price filter
        price_filter = price_filter.lower()
        if price_filter == "under_50":
            df = df[df["Price"] < 50]
        elif price_filter == "over_50":
            df = df[df["Price"] >= 50]

        df = df.sort_values("Price", ascending=False)
        final = df["Symbol"].head(limit).tolist()
        print(f"✅ Returning {len(final)} tickers in price range: {price_filter}")
        return final

    except Exception as e:
        print(f"❌ Screener failed: {e}")
        return [
            "PLTR", "SOFI", "U", "CHPT", "FUBO", "BBD", "MARA", "RIOT", "WBD", "RUN",
            "OPEN", "LUMN", "VZ", "T", "BB", "FCEL", "NOK", "SIRI", "PENN", "DNA", "SPWR",
            "WISH", "CVNA", "GPRO", "TLRY", "NKLA", "AUR", "RIVN", "HOOD", "F"
        ]

















