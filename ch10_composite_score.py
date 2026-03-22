"""
Chapter 10: Composite Fundamental Score
Combines the best surviving metrics from Chapters 1-9 into a single score.

Composite_i = z(ROA) + z(GP/TA) + z(EY) + z(OCF/NI) - z(Accruals)

Each component captures a different dimension: profitability (ROA),
business quality (GP/TA), cheapness (EY), earnings quality (OCF/NI),
and accounting integrity (-accruals).
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore

def get_fundamentals(ticker):
    """Extract the five fundamental metrics for one stock."""
    stock = yf.Ticker(ticker)
    inc, bs, cf = stock.income_stmt, stock.balance_sheet, stock.cashflow
    info = stock.info

    def g(df, n, c=0):
        return float(df.loc[n].iloc[c]) if n in df.index else None

    ni = g(inc, 'Net Income')
    ta = g(bs, 'Total Assets')
    gp = g(inc, 'Gross Profit')
    ebit = g(inc, 'EBIT')
    ocf = g(cf, 'Operating Cash Flow')
    market_cap = info.get('marketCap', None)
    total_debt = g(bs, 'Total Debt') or 0
    cash = g(bs, 'Cash And Cash Equivalents') or 0
    ev = (market_cap + total_debt - cash) if market_cap else None

    roa = ni / ta * 100 if ni and ta and ta > 0 else None
    gp_ta = gp / ta * 100 if gp and ta and ta > 0 else None
    ey = ebit / ev * 100 if ebit and ev and ev > 0 else None
    ocf_ni = ocf / ni if ocf and ni and ni != 0 else None
    accruals = (ni - ocf) / ta * 100 if all(v is not None for v in [ni, ocf, ta]) and ta > 0 else None

    return {'ROA': roa, 'GP_TA': gp_ta, 'EY': ey, 'OCF_NI': ocf_ni, 'Accruals': accruals}

if __name__ == "__main__":
    tickers = ['AAPL','MSFT','GOOG','AMZN','META','NVDA','V','JNJ',
               'WMT','PG','MA','HD','CSCO','MRK','UNH','ACN','BA','F',
               'INTC','GM','XOM','CVX','CAT','CL','KO','PEP','ABT','TXN',
               'QCOM','IBM','VZ','GS','LMT','HON','DE','LOW','COST',
               'NKE','MCD','BLK','ITW','NEE','APD','PM']
    raw = {}
    for tk in tickers:
        try:
            raw[tk] = get_fundamentals(tk)
        except Exception as e:
            print(f"  {tk}: ERROR - {e}")

    df = pd.DataFrame(raw).T.dropna()
    print(f"Computing composite for {len(df)} stocks with complete data\n")

    # Z-score each metric
    for col in ['ROA', 'GP_TA', 'EY', 'OCF_NI']:
        df[f'z_{col}'] = zscore(df[col])
    df['z_Accruals'] = zscore(df['Accruals'])

    # Composite = z(ROA) + z(GP/TA) + z(EY) + z(OCF/NI) - z(Accruals)
    df['Composite'] = (df['z_ROA'] + df['z_GP_TA'] + df['z_EY']
                       + df['z_OCF_NI'] - df['z_Accruals'])
    df = df.sort_values('Composite', ascending=False)

    # Display
    top = df.head(10)
    bottom = df.tail(5)
    show = pd.concat([top, bottom])
    print(show[['ROA','GP_TA','EY','OCF_NI','Accruals','Composite']].to_string(float_format='%.1f'))

    # Plot
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ['#3498db' if v >= 0 else '#e74c3c' for v in show['Composite']]
    ax.barh(range(len(show)), show['Composite'], color=colors)
    ax.set_yticks(range(len(show)))
    ax.set_yticklabels(show.index)
    ax.set_xlabel('Composite Fundamental Score')
    ax.set_title('Multi-factor fundamental ranking')
    ax.axvline(0, color='black', linewidth=0.5)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig('fig_ch10_composite.png', dpi=150)
    plt.show()
