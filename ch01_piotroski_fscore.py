"""
Chapter 1: Piotroski F-Score
Piotroski, 'Value Investing: The Use of Historical Financial Statement
Information to Separate Winners from Losers', JAR, 2000. 4,200+ citations.

Nine binary signals scoring profitability (F1-F4), leverage/liquidity (F5-F7),
and operating efficiency (F8-F9). Applied to the cheapest quintile of stocks
by book-to-market, buying high-F and shorting low-F returned 23% per year
in the 1976-1996 sample.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def g(df, n, c=0):
    """Safe getter for financial statement line items."""
    return float(df.loc[n].iloc[c]) if n in df.index else None

def piotroski_fscore(ticker):
    """Compute the 9-point Piotroski F-Score for a single stock."""
    stock = yf.Ticker(ticker)
    bs, inc, cf = stock.balance_sheet, stock.income_stmt, stock.cashflow

    score = 0
    ni, ta = g(inc, 'Net Income'), g(bs, 'Total Assets')
    ni_p, ta_p = g(inc, 'Net Income', 1), g(bs, 'Total Assets', 1)
    ocf = g(cf, 'Operating Cash Flow')

    # F1: ROA > 0
    if ni and ta and ni / ta > 0:
        score += 1
    # F2: Operating cash flow > 0
    if ocf and ocf > 0:
        score += 1
    # F3: ROA improving
    if all([ni, ta, ni_p, ta_p]) and ni / ta > ni_p / ta_p:
        score += 1
    # F4: Cash flow > net income (accruals quality)
    if ocf and ni and ocf > ni:
        score += 1

    # F5: Leverage decreasing
    ltd = g(bs, 'Long Term Debt')
    ltd_p = g(bs, 'Long Term Debt', 1)
    if all([ltd, ta, ltd_p, ta_p]) and ltd / ta < ltd_p / ta_p:
        score += 1

    # F6: Current ratio improving
    ca, cl = g(bs, 'Current Assets'), g(bs, 'Current Liabilities')
    ca_p, cl_p = g(bs, 'Current Assets', 1), g(bs, 'Current Liabilities', 1)
    if all([ca, cl, ca_p, cl_p]) and cl > 0 and cl_p > 0:
        if ca / cl > ca_p / cl_p:
            score += 1

    # F7: No dilution (shares outstanding did not increase)
    shares = g(bs, 'Ordinary Shares Number')
    shares_p = g(bs, 'Ordinary Shares Number', 1)
    if shares and shares_p and shares <= shares_p:
        score += 1

    # F8: Gross margin improving
    gp = g(inc, 'Gross Profit')
    rev = g(inc, 'Total Revenue')
    gp_p = g(inc, 'Gross Profit', 1)
    rev_p = g(inc, 'Total Revenue', 1)
    if all([gp, rev, gp_p, rev_p]) and rev > 0 and rev_p > 0:
        if gp / rev > gp_p / rev_p:
            score += 1

    # F9: Asset turnover improving
    if all([rev, ta, rev_p, ta_p]) and ta > 0 and ta_p > 0:
        if rev / ta > rev_p / ta_p:
            score += 1

    return score

if __name__ == "__main__":
    tickers = ['AAPL','MSFT','GOOG','AMZN','META','NVDA','JPM','V','JNJ',
               'WMT','PG','MA','HD','CSCO','PM','RTX','BA','F','INTC','GE',
               'XOM','CVX','CAT','ABT','MRK','PFE','UNH','CL','KO','PEP',
               'ACN','BLK','ITW','NEE','APD','GM','DIS','NFLX','CRM','ADBE',
               'TXN','QCOM','LMT','MMM','IBM','VZ','T','WFC','GS','MS',
               'C','BAC','AXP','COST','LOW','TGT','NKE','SBUX','MCD','CMG',
               'DE','HON','UPS','FDX','RTX','LIN','SHW','ECL','EMR','GD']
    scores = {}
    for tk in tickers:
        try:
            scores[tk] = piotroski_fscore(tk)
            print(f"  {tk}: F-Score = {scores[tk]}")
        except Exception as e:
            print(f"  {tk}: ERROR - {e}")

    if scores:
        s = pd.Series(scores).sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(s.values, bins=range(0, 11), edgecolor='black', alpha=0.7)
        ax.set_xlabel('Piotroski F-Score')
        ax.set_ylabel('Number of stocks')
        ax.set_title(f'F-Score distribution, {len(s)} large-cap US stocks')
        plt.tight_layout()
        plt.savefig('fig_ch01_fscore.png', dpi=150)
        plt.show()
        print(f"\nMedian = {s.median():.0f}")
        print(f"High F (>=8): {list(s[s >= 8].index)}")
        print(f"Low F  (<=2): {list(s[s <= 2].index)}")
