"""
Chapter 3: Altman Z-Score
Altman, 'Financial Ratios, Discriminant Analysis and the Prediction of
Corporate Bankruptcy', Journal of Finance, 1968. 18,000+ citations.

Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
X1 = Working Capital / Total Assets (liquidity)
X2 = Retained Earnings / Total Assets (cumulative profitability)
X3 = EBIT / Total Assets (current profitability, highest weight)
X4 = Market Cap / Total Liabilities (solvency)
X5 = Revenue / Total Assets (efficiency)

Z > 2.99: safe zone. Z < 1.81: distress zone. Between: grey zone.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def altman_zscore(ticker):
    """Compute the Altman Z-Score for a single stock."""
    stock = yf.Ticker(ticker)
    bs, inc = stock.balance_sheet, stock.income_stmt
    info = stock.info

    def g(df, n, c=0):
        return float(df.loc[n].iloc[c]) if n in df.index else None

    ta = g(bs, 'Total Assets')
    if not ta or ta == 0:
        return None

    ca = g(bs, 'Current Assets') or 0
    cl = g(bs, 'Current Liabilities') or 0
    re = g(bs, 'Retained Earnings') or 0
    ebit = g(inc, 'EBIT') or 0
    rev = g(inc, 'Total Revenue') or 0
    market_cap = info.get('marketCap', 0) or 0
    tl = g(bs, 'Total Liabilities Net Minority Interest') or g(bs, 'Total Debt') or 0

    x1 = (ca - cl) / ta
    x2 = re / ta
    x3 = ebit / ta
    x4 = market_cap / tl if tl > 0 else 10.0
    x5 = rev / ta

    z = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + 1.0*x5
    return z

if __name__ == "__main__":
    tickers = ['AAPL','MSFT','GOOG','AMZN','META','NVDA','JPM','V','JNJ',
               'WMT','PG','MA','HD','CSCO','PM','MRK','UNH','ACN','BA',
               'F','INTC','GM','XOM','CVX','CAT','CL','KO','PEP','ABT',
               'TXN','QCOM','IBM','VZ','WFC','GS','LMT','HON','UPS','DE',
               'LOW','COST','NKE','MCD','CRM','ADBE','BLK','ITW','NEE','APD',
               'T','C','BAC','AXP','MS','GE','RTX','LIN','SHW','MMM',
               'PFE','DIS','NFLX','SBUX','CMG','FDX','EMR','GD','ECL','TGT']
    scores = {}
    for tk in tickers:
        try:
            z = altman_zscore(tk)
            if z is not None:
                scores[tk] = z
                zone = "SAFE" if z > 2.99 else "DISTRESS" if z < 1.81 else "GREY"
                print(f"  {tk}: Z = {z:.2f} [{zone}]")
        except Exception as e:
            print(f"  {tk}: ERROR - {e}")

    if scores:
        s = pd.Series(scores).sort_values()
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(s.values, bins=30, edgecolor='black', alpha=0.7)
        ax.axvline(1.81, color='red', linestyle='--', label='Distress (1.81)')
        ax.axvline(2.99, color='green', linestyle='--', label='Safe (2.99)')
        ax.set_xlabel('Altman Z-Score')
        ax.set_ylabel('Count')
        ax.set_title(f'Z-Score distribution, {len(s)} US stocks')
        ax.legend()
        plt.tight_layout()
        plt.savefig('fig_ch03_zscore.png', dpi=150)
        plt.show()
