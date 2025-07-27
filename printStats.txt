import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def analyze_simulation(trade_log):
    # Check if trade_log has P&L entries
    if not trade_log or not any('total_pnl' in t for t in trade_log):
        print("Error: trade_log is empty or contains no P&L entries")
        return
    
    # Convert trade log to DataFrame, keeping only P&L entries
    df = pd.DataFrame([t for t in trade_log if 'total_pnl' in t])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Debug: Log trade frequency and P&L range
    trades = [t for t in trade_log if 'trade_value' in t]
    print(f"Total trades: {len(trades)}")
    print(f"P&L range: {df['total_pnl'].min():.2f} - {df['total_pnl'].max():.2f}")
    
    # Compute daily returns
    df['daily_pnl'] = df['total_pnl'].diff().fillna(0)
    df['daily_returns'] = df['daily_pnl'] / df['total_pnl'].shift(1).replace(0, 1)
    
    # Debug: Log returns variability and non-zero daily returns count
    print(f"Non-zero daily returns count: {(df['daily_pnl'] != 0).sum()}")
    print(f"Daily returns range: {df['daily_returns'].min():.4f} - {df['daily_returns'].max():.4f}")
    print(f"Daily returns std: {df['daily_returns'].std():.4f}")
    
    # Performance Metrics
    mean_pnl = df['total_pnl'].mean()
    median_pnl = df['total_pnl'].median()
    std_pnl = df['total_pnl'].std()
    
    # Sharpe Ratio (assuming risk-free rate = 0)
    sharpe_ratio = (df['daily_returns'].mean() * 252 ** 0.5) / (df['daily_returns'].std() + 1e-10)
    
    # Maximum Drawdown
    cumulative_pnl = df['total_pnl'].cumsum()
    running_max = cumulative_pnl.cummax()
    drawdown = cumulative_pnl - running_max
    max_drawdown = drawdown.min()
    
    # Debug: Log drawdown range
    print(f"Drawdown range: {drawdown.min():.2f} - {drawdown.max():.2f}")
    
    # Rolling VaR and Expected Shortfall (95%) with 50-row window
    window = 50
    df['var_95'] = df['daily_returns'].rolling(window=window, min_periods=10).quantile(0.05)
    df['expected_shortfall'] = df['daily_returns'].rolling(window=window, min_periods=10).apply(
        lambda x: x[x <= x.quantile(0.05)].mean() if len(x[x <= x.quantile(0.05)]) > 0 else 0
    )
    
    # Fill NaN values for initial rows
    df['var_95'] = df['var_95'].fillna(0)
    df['expected_shortfall'] = df['expected_shortfall'].fillna(0)
    
    # Add other metrics to DataFrame
    df['mean_pnl'] = mean_pnl
    df['median_pnl'] = median_pnl
    df['std_pnl'] = std_pnl
    df['sharpe_ratio'] = sharpe_ratio
    df['max_drawdown'] = max_drawdown
    
    # Save to CSV
    df[['total_pnl', 'mean_pnl', 'median_pnl', 'std_pnl', 'sharpe_ratio', 
        'max_drawdown', 'var_95', 'expected_shortfall']].to_csv('pnl_output.csv')
    
    # Generate plots
    plt.figure(figsize=(10, 6))
    plt.plot(cumulative_pnl, label='Cumulative P&L', color='#1f77b4')
    plt.title('Cumulative P&L Curve')
    plt.xlabel('Timestamp')
    plt.ylabel('P&L')
    plt.legend()
    plt.grid(True)
    plt.savefig('cumulative_pnl.png')
    plt.close()
    
    plt.figure(figsize=(10, 6))
    plt.plot(drawdown, label='Drawdown', color='#d62728')
    plt.title('Drawdown Curve')
    plt.xlabel('Timestamp')
    plt.ylabel('Drawdown')
    plt.legend()
    plt.grid(True)
    plt.savefig('drawdown.png')
    plt.close()

if __name__ == "__main__":
    from Simulator import Simulator
    simulator = Simulator()
    analyze_simulation(simulator.trade_log)
