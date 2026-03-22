"""
Chapter 4: Novy-Marx Gross Profitability
Novy-Marx, 'The Other Side of Value: The Gross Profitability Premium',
Journal of Financial Economics, 2013. 2,200+ citations.

Gross Profitability = Gross Profit / Total Assets
The cleanest measure of economic profitability. Harder to manipulate than
net income, ROE, or EBIT. Stocks in the top quintile outperformed the
bottom quintile by 4-5% per year from 1963 to 2010.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def gross_profitability(ticker):
    """Compute Gross Profit / Total Assets for a single stock."""
    stock = yf.Ticker(ticker)
    inc, bs = stock.income_stmt, stock.balance_sheet
    gp = float(inc.loc['Gross Profit'].iloc[0]) if 'Gross Profit' in inc.index else None
    ta = float(bs.loc['Total Assets'].iloc[0]) if 'Total Assets' in bs.index else None
    if gp and ta and ta > 0:
        return gp / ta * 100
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
            gp = gross_profitability(tk)
            if gp is not None:
                results[tk] = gp
                print(f"  {tk}: GP/TA = {gp:.1f}%")
        except Exception as e:
            print(f"  {tk}: ERROR - {e}")

    if results:
        s = pd.Series(results).sort_values(ascending=False)
        median = s.median()
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['#3498db' if v >= median else '#e74c3c' for v in s.values]
        ax.bar(range(len(s)), s.values, color=colors)
        ax.axhline(median, color='gray', linestyle='--', alpha=0.5, label=f'Median ({median:.1f}%)')
        ax.set_xticks(range(len(s)))
        ax.set_xticklabels(s.index, rotation=90, fontsize=7)
        ax.set_ylabel('Gross Profit / Total Assets (%)')
        ax.set_title(f'Gross profitability ranking, {len(s)} stocks')
        ax.legend()
        plt.tight_layout()
        plt.savefig('fig_ch04_gross_profitability.png', dpi=150)
        plt.show()
