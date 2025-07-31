import pandas as pd
import yfinance as yf
from scanner.technicals import calculate_technicals, is_valid_setup

def backtest_strategy(df, setup_function, initial_balance=10000, risk_per_trade=0.01):
    if df is None or df.empty or len(df) < 50:
        return None

    balance = initial_balance
    trades = []

    for i in range(len(df) - 5):
        window = df.iloc[:i+1].copy()
        if setup_function(window):
            entry_price = df.iloc[i]['Close']
            exit_price = df.iloc[i + 5]['Close']
            position_size = balance * risk_per_trade / entry_price
            pnl = (exit_price - entry_price) * position_size
            balance += pnl

            trades.append({
                'entry_date': df.index[i],
                'exit_date': df.index[i + 5],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl': pnl,
                'balance': balance
            })

    return pd.DataFrame(trades)

def summarize_backtest(results_df):
    if results_df is None or results_df.empty:
        return {
            'total_return': 0,
            'win_rate': 0,
            'avg_gain': 0,
            'max_drawdown': 0,
            'total_trades': 0,
            'summary': "No trades were triggered during this period."
        }

    total_return = results_df['balance'].iloc[-1] - results_df['balance'].iloc[0]
    win_rate = (results_df['pnl'] > 0).mean()
    avg_pnl = results_df['pnl'].mean()
    max_drawdown = results_df['balance'].cummax() - results_df['balance']
    max_dd = max_drawdown.max()

    summary = (
        f"📈 In this period, the system grew your account by **${total_return:,.2f}**.\n"
        f"💰 **{win_rate*100:.1f}%** of trades made money.\n"
        f"📊 Average gain per trade: **${avg_pnl:.2f}**.\n"
        f"🛡️ Worst dip in account: **-${max_dd:.2f}**.\n"
    )

    return {
        'total_return': round(total_return, 2),
        'win_rate': round(win_rate * 100, 1),
        'avg_gain': round(avg_pnl, 2),
        'max_drawdown': round(max_dd, 2),
        'total_trades': len(results_df),
        'summary': summary
    }

def run_backtest(tickers, period="6mo", min_gain=0.05):
    all_trades = []
    setups_found = 0
    successful = 0

    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, interval="1d", progress=False)
            if df.empty:
                continue

            df = calculate_technicals(df)
            if not is_valid_setup(df):
                continue

            setups_found += 1
            result = backtest_strategy(df, is_valid_setup)
            if result is not None and not result.empty:
                all_trades.append(result)
                last_trade = result.iloc[-1]
                if last_trade["pnl"] > min_gain * 10000:  # 1% of 10k
                    successful += 1
        except Exception:
            continue

    if not all_trades:
        return {
            'total': len(tickers),
            'setups_found': 0,
            'successful': 0,
            'summary': "No valid setups found during backtest.",
            'details': pd.DataFrame()
        }

    trades_df = pd.concat(all_trades)
    stats = summarize_backtest(trades_df)

    return {
        'total': len(tickers),
        'setups_found': setups_found,
        'successful': successful,
        'summary': stats["summary"],
        'details': trades_df,
        'stats': stats
    }
