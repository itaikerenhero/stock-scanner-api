from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import random
from typing import List, Dict, Any
from scanner import data_loader, technicals, backtester
from llm.summaries import summarize_stock

app = FastAPI(title="Stock Scanner API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_scanner_api(price_filter: str = "All", max_results: int = 10):
    """Core scanner logic extracted from Streamlit app"""
    tickers = data_loader.get_tickers(price_filter)
    random.shuffle(tickers)
    
    results = []
    for ticker in tickers:
        try:
            df = data_loader.get_data(ticker)
            if df.empty:
                continue

            latest_price = df["Close"].iloc[-1]
            
            if price_filter == "Under $50" and latest_price > 50:
                continue
            elif price_filter == "Over $50" and latest_price <= 50:
                continue

            df = technicals.calculate_technicals(df)
            if not technicals.is_valid_setup(df):
                continue
                
            setup = technicals.describe_setup(df)
            latest = df.iloc[-1]
            score = calculate_setup_score(latest, setup)
            
            results.append({
                "ticker": ticker,
                "score": score,
                "type": setup.replace(" setup", "").title(),
                "price": round(latest_price, 2),
                "rsi": round(latest.get('RSI', 0), 1) if not pd.isna(latest.get('RSI', 0)) else None
            })
            
        except Exception as e:
            print(f"⚠️ Error with {ticker}: {e}")
            continue
            
        if len(results) >= max_results:
            break
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def calculate_setup_score(latest_row, setup_type):
    """Calculate score based on technical indicators (0-100 scale)"""
    score = 50  # Base score
    
    if "Breakout" in setup_type:
        score += 25
    elif "Bullish momentum" in setup_type:
        score += 20
    elif "Pullback" in setup_type:
        score += 15
    
    rsi = latest_row.get('RSI', 50)
    if not pd.isna(rsi):
        if 50 <= rsi <= 70:
            score += 15
        elif rsi > 70:
            score -= 5
        elif rsi < 30:
            score -= 10
    
    if latest_row.get('Volume_Spike', False):
        score += 10
    
    if latest_row.get('Above_SMA20', False):
        score += 5
    
    return min(100, max(0, int(score)))

def get_summary_api(ticker: str):
    """Core summary logic extracted from Streamlit app"""
    try:
        df = data_loader.get_data(ticker)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        df = technicals.calculate_technicals(df)
        summary, score = summarize_stock(ticker, df)
        
        return {
            "ticker": ticker,
            "summary": summary,
            "score": score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

def get_chart_data_api(ticker: str, period: str = "6mo"):
    """Extract chart data for candlestick plotting"""
    try:
        df = data_loader.get_data(ticker, period=period)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        df = technicals.calculate_technicals(df)
        
        chart_data = {
            "ticker": ticker,
            "dates": [date.strftime("%Y-%m-%d") for date in df.index],
            "candles": [
                {
                    "open": round(row['Open'], 2),
                    "high": round(row['High'], 2),
                    "low": round(row['Low'], 2),
                    "close": round(row['Close'], 2),
                    "volume": int(row['Volume'])
                }
                for _, row in df.iterrows()
            ],
            "sma_20": [round(val, 2) if not pd.isna(val) else None for val in df['SMA_20']],
            "sma_50": [round(val, 2) if not pd.isna(val) else None for val in df['SMA_50']],
            "rsi": [round(val, 1) if not pd.isna(val) else None for val in df.get('RSI', [])]
        }
        
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chart data: {str(e)}")

@app.get("/scan")
async def scan_stocks(
    price_filter: str = Query("All", description="Stock price filter: All, Under $50, Over $50"),
    limit: int = Query(10, description="Maximum number of results")
):
    """Scan for high-potential stocks using the same logic as the Streamlit app"""
    try:
        results = run_scanner_api(price_filter, limit)
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scanner error: {str(e)}")

@app.get("/summary")
async def get_summary(ticker: str = Query(..., description="Stock ticker symbol")):
    """Get AI-generated summary for a specific ticker"""
    return get_summary_api(ticker.upper())

@app.get("/chart")
async def get_chart(
    ticker: str = Query(..., description="Stock ticker symbol"),
    period: str = Query("6mo", description="Time period: 1mo, 3mo, 6mo, 1y, 2y")
):
    """Get candlestick chart data with technical indicators"""
    return get_chart_data_api(ticker.upper(), period)

@app.get("/backtest")
async def get_backtest(
    tickers: str = Query(None, description="Comma-separated list of tickers (e.g., 'AAPL,MSFT,TSLA'). If not provided, uses default universe."),
    period: str = Query("1y", description="Backtest period: 3mo, 6mo, 1y, 2y"),
    min_gain: float = Query(5.0, description="Minimum gain percentage to count as success (e.g., 5.0 for 5%)")
):
    """Run backtest on the scanner strategy with custom tickers and filters"""
    try:
        # Process tickers input
        if tickers:
            ticker_list = [ticker.strip().upper() for ticker in tickers.split(",") if ticker.strip()]
        else:
            # If no tickers provided, use default universe from data_loader
            ticker_list = data_loader.get_tickers(price_filter="All")

        # Convert min_gain from percentage to decimal (5% -> 0.05)
        min_gain_decimal = min_gain / 100

        # Run the backtest using backtester.py logic
        results = backtester.run_backtest(
            tickers=ticker_list,
            period=period,
            min_gain=min_gain_decimal
        )
        
        # Calculate win rate
        win_rate = (
            round((results['successful'] / results['setups_found']) * 100, 2)
            if results['setups_found'] > 0
            else 0
        )

        # Get S&P 500 return for comparison
        sp500_return = 0
        try:
            spy_df = data_loader.get_data("SPY", period=period)
            if not spy_df.empty:
                sp500_start = spy_df['Close'].iloc[0]
                sp500_end = spy_df['Close'].iloc[-1]
                sp500_return = round(((sp500_end - sp500_start) / sp500_start) * 100, 2)
        except Exception as e:
            print(f"Error getting SPY data: {e}")
            
        return {
            "status": "success",
            "input_params": {
                "tickers_count": len(ticker_list),
                "period": period,
                "min_gain_percent": min_gain
            },
            "results": {
                "total_stocks_checked": results['total'],
                "valid_setups_found": results['setups_found'],
                "successful_trades": results['successful'],
                "win_rate_percent": win_rate,
                "scanner_return": results.get('stats', {}).get('total_return', 0),
                "sp500_return": sp500_return
            },
            "details": {
                "trades": results.get('details', pd.DataFrame()).to_dict('records') if not results.get('details', pd.DataFrame()).empty else [],
                "stats": results.get('stats', {}),
                "summary": results.get('summary', "No backtest results available.")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Stock Scanner API is running",
        "version": "1.0.0",
        "endpoints": ["/scan", "/summary", "/chart", "/backtest"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
