"""
Chapter 8: Cash Flow vs. Net Income
Dechow, 'Earnings Management: Reconciling the Views of Accounting Academics,
Practitioners, and Regulators', Accounting Horizons, 2000. 3,500+ citations.

Cash Conversion = Operating Cash Flow / Net Income
Healthy range: 1.0 to 1.5. Below 0.7: earnings may be low quality.
Above 2.0: large depreciation relative to earnings (capital-intensive).
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def cash_conversion(ticker):
    """Compute OCF/NI ratio for a single stock."""
    stock = yf.Ticker(ticker)
    inc, cf = stock.income_stmt, stock.cashflow
    ni = float(inc.loc['Net Income'].iloc[0]) if 'Net Income' in inc.index else None
    ocf = float(cf.loc['Operating Cash Flow'].iloc[0]) if 'Operating Cash Flow' in cf.index else None
    if ni and ocf:
        return {'net_income': ni, 'ocf': ocf, 'ratio': ocf / ni if ni != 0 else None}
    return None

if __name__ == "__main__":
    tickers = ['AAPL','MSFT','GOOG','AMZN','META','NVDA','JPM','V','JNJ',
               'WMT','PG','MA','HD','CSCO','MRK','UNH','ACN','BA','F',
               'INTC','GM','XOM','CVX','CAT','CL','KO','PEP','ABT','TXN',
               'QCOM','IBM','VZ','WFC','GS','LMT','HON','DE','LOW','COST']
    results = {}
    for tk in tickers:
        try:
            r = cash_conversion(tk)
            if r and r['ratio'] is not None:
                results[tk] = r
                quality = "HIGH" if r['ratio'] >= 1.0 else "LOW" if r['ratio'] < 0.7 else "OK"
                print(f"  {tk}: OCF/NI = {r['ratio']:.2f} [{quality}]")
        except Exception as e:
            print(f"  {tk}: ERROR - {e}")

    if results:
        df = pd.DataFrame(results).T
        df['ni_b'] = df['net_income'] / 1e9
        df['ocf_b'] = df['ocf'] / 1e9
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.scatter(df['ni_b'], df['ocf_b'], s=40, alpha=0.7)
        lim = max(abs(df['ni_b']).max(), abs(df['ocf_b']).max()) * 1.1
        ax.plot([-lim, lim], [-lim, lim], 'r--', alpha=0.5, label='OCF = Net Income')
        for tk in df.index:
            ax.annotate(tk, (df.loc[tk,'ni_b'], df.loc[tk,'ocf_b']), fontsize=6)
        ax.set_xlabel('Net Income ($B)')
        ax.set_ylabel('Operating Cash Flow ($B)')
        ax.set_title('Cash vs reported earnings: above the line = cash-backed')
        ax.legend()
        plt.tight_layout()
        plt.savefig('fig_ch08_cashflow.png', dpi=150)
        plt.show()
