from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scanner.filters import get_tickers
from llm.summaries import summarize_stock
from scanner.backtester import get_backtest_data
from scanner.technicals import get_chart_data

app = FastAPI(
    title="Stock Scanner API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Stock Scanner API is running",
        "version": "1.0.0",
        "endpoints": ["/scan", "/summary", "/chart", "/backtest"]
    }

@app.get("/scan")
def scan():
    return get_tickers(price_filter=None)  # Or add query param for price filter

@app.get("/summary")
def summary(ticker: str):
    return summarize_stock(ticker, setup_info={}, prompt_override=None)

@app.get("/chart")
def chart(ticker: str):
    return get_chart_data(ticker)

@app.get("/backtest")
def backtest():
    return get_backtest_data()
