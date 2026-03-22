"""
Chapter 5: Sloan Accruals Anomaly
Sloan, 'Do Stock Prices Fully Reflect Information in Accruals and Cash
Flows About Future Earnings?', The Accounting Review, 1996. 6,000+ citations.

Accruals = (Net Income - Operating Cash Flow) / Total Assets
Negative accruals (OCF > NI) = high quality: earnings backed by cash.
Positive accruals (NI > OCF) = low quality: revenue recognized but not collected.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def sloan_accruals(ticker):
    """Compute accruals ratio for a single stock."""
    stock = yf.Ticker(ticker)
    inc, cf, bs = stock.income_stmt, stock.cashflow, stock.balance_sheet
    ni = float(inc.loc['Net Income'].iloc[0]) if 'Net Income' in inc.index else None
    ocf = float(cf.loc['Operating Cash Flow'].iloc[0]) if 'Operating Cash Flow' in cf.index else None
    ta = float(bs.loc['Total Assets'].iloc[0]) if 'Total Assets' in bs.index else None
    if all(v is not None for v in [ni, ocf, ta]) and ta > 0:
        return (ni - ocf) / ta * 100
    return None

if __name__ == "__main__":
    tickers = ['AAPL','MSFT','GOOG','AMZN','META','NVDA','JPM','V','JNJ',
               'WMT','PG','MA','HD','CSCO','MRK','UNH','ACN','BA','F',
               'INTC','GM','XOM','CVX','CAT','CL','KO','PEP','ABT','TXN',
               'QCOM','IBM','VZ','WFC','GS','LMT','HON','DE','LOW','COST',
               'NKE','MCD','BLK','ITW','NEE','APD','PM','UPS','CRM','ADBE']
    results = {}
    for tk in tickers:
        try:
            acc = sloan_accruals(tk)
            if acc is not None:
                results[tk] = acc
                quality = "CASH-BACKED" if acc < 0 else "PAPER EARNINGS"
                print(f"  {tk}: Accruals/TA = {acc:.1f}% [{quality}]")
        except Exception as e:
            print(f"  {tk}: ERROR - {e}")

    if results:
        s = pd.Series(results).sort_values()
        fig, ax = plt.subplots(figsize=(14, 4))
        colors = ['#2ecc71' if v < 0 else '#e74c3c' for v in s.values]
        ax.barh(range(len(s)), s.values, color=colors)
        ax.axvline(0, color='black', linewidth=0.5)
        ax.set_yticks(range(len(s)))
        ax.set_yticklabels(s.index, fontsize=6)
        ax.set_xlabel('Accruals / Total Assets (%)')
        ax.set_title('Accruals quality: negative = cash-backed, positive = paper earnings')
        plt.tight_layout()
        plt.savefig('fig_ch05_accruals.png', dpi=150)
        plt.show()
