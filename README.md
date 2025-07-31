# Stock Scanner API 📈

A FastAPI-based REST API that provides endpoints for stock scanning, technical analysis, and backtesting. This API exposes the core functionality of our stock scanning system.

## 🚀 Features

- Real-time stock scanning with technical indicators
- AI-powered stock summaries and analysis
- Candlestick chart data with technical overlays
- Strategy backtesting with S&P 500 comparison

## 🛠 API Endpoints

### GET /scan
Scans for high-potential stocks based on technical setups.

```bash
curl "http://localhost:8000/scan?price_filter=All&limit=10"
```

**Parameters:**
- `price_filter`: "All", "Under $50", or "Over $50"
- `limit`: Maximum number of results (default: 10)

**Response:**
```json
{
    "status": "success",
    "count": 3,
    "results": [
        {
            "ticker": "AAPL",
            "score": 92,
            "type": "Breakout",
            "price": 175.25,
            "rsi": 65.4
        }
    ]
}
```

### GET /summary
Get AI-generated analysis for a specific stock.

```bash
curl "http://localhost:8000/summary?ticker=AAPL"
```

**Parameters:**
- `ticker`: Stock symbol (required)

**Response:**
```json
{
    "ticker": "AAPL",
    "summary": "Technical analysis of the stock...",
    "score": 3
}
```

### GET /chart
Get candlestick chart data with technical indicators.

```bash
curl "http://localhost:8000/chart?ticker=AAPL&period=6mo"
```

**Parameters:**
- `ticker`: Stock symbol (required)
- `period`: Time period (1mo, 3mo, 6mo, 1y, 2y)

**Response:**
```json
{
    "ticker": "AAPL",
    "dates": ["2024-01-01", ...],
    "candles": [
        {
            "open": 170.25,
            "high": 172.50,
            "low": 169.75,
            "close": 171.20,
            "volume": 75000000
        }
    ],
    "sma_20": [170.50, ...],
    "sma_50": [168.75, ...],
    "rsi": [65.4, ...]
}
```

### GET /backtest
Run backtesting analysis on a set of stocks.

```bash
curl "http://localhost:8000/backtest?tickers=AAPL,MSFT,TSLA&period=1y&min_gain=5.0"
```

**Parameters:**
- `tickers`: Comma-separated list of tickers (optional, uses default universe if not provided)
- `period`: Backtest period (3mo, 6mo, 1y, 2y)
- `min_gain`: Minimum gain percentage to count as success (e.g., 5.0 for 5%)

**Response:**
```json
{
    "status": "success",
    "input_params": {
        "tickers_count": 3,
        "period": "1y",
        "min_gain_percent": 5.0
    },
    "results": {
        "total_stocks_checked": 3,
        "valid_setups_found": 2,
        "successful_trades": 1,
        "win_rate_percent": 50.0,
        "scanner_return": 15.5,
        "sp500_return": 8.2
    },
    "details": {
        "trades": [...],
        "stats": {...},
        "summary": "Backtest results summary..."
    }
}
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd stock_scanner_ai
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the API

Start the FastAPI server:
```bash
uvicorn API.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## 📚 Documentation

Full API documentation is available at `/docs` or `/redoc` when the server is running.

## 🔒 Environment Variables

Required environment variables:
- `GROQ_API_KEY`: API key for Groq LLM service (for AI summaries)

## 🛠 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/): Modern, fast web framework
- [pandas-ta](https://github.com/twopirllc/pandas-ta): Technical analysis library
- [yfinance](https://github.com/ranaroussi/yfinance): Yahoo Finance data
- [Groq](https://groq.com/): LLM for AI analysis

## 📝 Notes

- The API is designed to work alongside the existing Streamlit UI
- All endpoints use the same core logic as the Streamlit app
- Rate limiting and authentication not implemented (add if needed)
- Consider caching for production use 