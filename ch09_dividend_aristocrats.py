"""
Chapter 9: Dividend Aristocrats Screen
S&P Dow Jones Indices, 'S&P 500 Dividend Aristocrats Index Methodology', 2005.

The Dividend Aristocrats are S&P 500 companies that have increased their
dividend every year for at least 25 consecutive years. The backtest
compares NOBL (ProShares S&P 500 Dividend Aristocrats ETF, inception 2013),
SCHD (Schwab US Dividend Equity ETF), and SPY.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    tickers = ['SPY', 'NOBL', 'SCHD']
    data = yf.download(tickers, start="2014-01-01", auto_adjust=True)['Close']
    if isinstance(data.columns, pd.MultiIndex):
        data = data.droplevel(0, axis=1)

    ret = data.pct_change().dropna()

    print("Dividend Aristocrats Backtest (2014-present)")
    print("=" * 55)
    for name in tickers:
        r = ret[name]
        ann_r = r.mean() * 252
        ann_v = r.std() * np.sqrt(252)
        sharpe = ann_r / ann_v
        cum = (1 + r).cumprod()
        mdd = (cum / cum.cummax() - 1).min()
        print(f"  {name:6s}  Ret={ann_r:.1%}  Vol={ann_v:.1%}  "
              f"Sharpe={sharpe:.2f}  MaxDD={mdd:.1%}")

    # Plot
    cum = (1 + ret).cumprod()
    fig, ax = plt.subplots(figsize=(10, 6))
    for tk in tickers:
        ax.plot(cum.index, cum[tk], label=tk)
    ax.set_yscale('log')
    ax.set_ylabel('Growth of $1 (log)')
    ax.set_title('Dividend Aristocrats (NOBL) vs SPY vs SCHD')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('fig_ch09_dividend_aristocrats.png', dpi=150)
    plt.show()
