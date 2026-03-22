"""
Chapter 6: Beneish M-Score
Beneish, 'The Detection of Earnings Manipulation', Financial Analysts
Journal, 1999. 3,000+ citations.

M = -4.84 + 0.92*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI
    + 0.115*DEPI - 0.172*SGAI + 4.679*TATA - 0.327*LVGI

M > -1.78: likely manipulator. M < -1.78: likely clean.
The model flagged Enron in 1998, two years before public disclosure.
"""
import yfinance as yf
import pandas as pd
import numpy as np

def g(df, n, c=0):
    """Safe getter for financial statement items."""
    return float(df.loc[n].iloc[c]) if n in df.index else None

def beneish_mscore(ticker):
    """Compute the 8-variable Beneish M-Score."""
    stock = yf.Ticker(ticker)
    inc, bs, cf = stock.income_stmt, stock.balance_sheet, stock.cashflow

    # Current year (c=0) and prior year (c=1)
    rev, rev_p = g(inc, 'Total Revenue', 0), g(inc, 'Total Revenue', 1)
    cogs, cogs_p = g(inc, 'Cost Of Revenue', 0), g(inc, 'Cost Of Revenue', 1)
    ni = g(inc, 'Net Income', 0)
    sga, sga_p = g(inc, 'Selling General And Administration', 0), g(inc, 'Selling General And Administration', 1)
    dep, dep_p = g(inc, 'Depreciation And Amortization In Income Statement', 0), g(inc, 'Depreciation And Amortization In Income Statement', 1)
    ta, ta_p = g(bs, 'Total Assets', 0), g(bs, 'Total Assets', 1)
    ca, ca_p = g(bs, 'Current Assets', 0), g(bs, 'Current Assets', 1)
    ppe, ppe_p = g(bs, 'Net PPE', 0), g(bs, 'Net PPE', 1)
    rec, rec_p = g(bs, 'Receivables', 0), g(bs, 'Receivables', 1)
    tl, tl_p = g(bs, 'Total Liabilities Net Minority Interest', 0), g(bs, 'Total Liabilities Net Minority Interest', 1)
    cl, cl_p = g(bs, 'Current Liabilities', 0), g(bs, 'Current Liabilities', 1)
    ltd, ltd_p = g(bs, 'Long Term Debt', 0), g(bs, 'Long Term Debt', 1)
    ocf = g(cf, 'Operating Cash Flow', 0)

    if not all([rev, rev_p, ta, ta_p]):
        return None, {}

    # DSRI: Days Sales in Receivables Index
    dsri = ((rec or 0)/rev) / ((rec_p or 0)/rev_p) if rev_p and rec_p else 1.0

    # GMI: Gross Margin Index
    gm = (rev - (cogs or 0)) / rev if rev else 0
    gm_p = (rev_p - (cogs_p or 0)) / rev_p if rev_p else 0
    gmi = gm_p / gm if gm > 0 else 1.0

    # AQI: Asset Quality Index
    hard = (ca or 0) + (ppe or 0)
    hard_p = (ca_p or 0) + (ppe_p or 0)
    aqi = (1 - hard/ta) / (1 - hard_p/ta_p) if ta_p and hard_p/ta_p < 1 else 1.0

    # SGI: Sales Growth Index
    sgi = rev / rev_p if rev_p else 1.0

    # DEPI: Depreciation Index
    dep_rate = (dep or 0) / ((dep or 0) + (ppe or 1))
    dep_rate_p = (dep_p or 0) / ((dep_p or 0) + (ppe_p or 1))
    depi = dep_rate_p / dep_rate if dep_rate > 0 else 1.0

    # SGAI: SGA Index
    sga_ratio = (sga or 0) / rev if rev else 0
    sga_ratio_p = (sga_p or 0) / rev_p if rev_p else 0
    sgai = sga_ratio / sga_ratio_p if sga_ratio_p > 0 else 1.0

    # TATA: Total Accruals to Total Assets
    tata = ((ni or 0) - (ocf or 0)) / ta if ta else 0

    # LVGI: Leverage Index
    lev = ((cl or 0) + (ltd or 0)) / ta if ta else 0
    lev_p = ((cl_p or 0) + (ltd_p or 0)) / ta_p if ta_p else 0
    lvgi = lev / lev_p if lev_p > 0 else 1.0

    m = (-4.84 + 0.92*dsri + 0.528*gmi + 0.404*aqi + 0.892*sgi
         + 0.115*depi - 0.172*sgai + 4.679*tata - 0.327*lvgi)

    components = {'DSRI': dsri, 'GMI': gmi, 'AQI': aqi, 'SGI': sgi,
                  'DEPI': depi, 'SGAI': sgai, 'TATA': tata, 'LVGI': lvgi}
    return m, components

if __name__ == "__main__":
    tickers = ['AAPL','MSFT','GOOG','AMZN','META','NVDA','JPM','V','JNJ',
               'WMT','PG','MA','HD','CSCO','MRK','UNH','ACN','BA','F',
               'INTC','GM','XOM','CVX','CAT','CL','KO','PEP','ABT','TXN']
    results = {}
    for tk in tickers:
        try:
            m, comp = beneish_mscore(tk)
            if m is not None:
                results[tk] = m
                flag = "*** FLAGGED ***" if m > -1.78 else "clean"
                print(f"  {tk}: M = {m:.2f} [{flag}]")
        except Exception as e:
            print(f"  {tk}: ERROR - {e}")

    if results:
        s = pd.Series(results).sort_values(ascending=False)
        print(f"\nFlagged (M > -1.78): {list(s[s > -1.78].index)}")
        print(f"Clean   (M < -1.78): {list(s[s <= -1.78].index)}")
