"""
Chapter 2: Greenblatt's Magic Formula
Greenblatt, 'The Little Book That Beats the Market', Wiley, 2005.

Two ratios: Earnings Yield (EBIT/EV) measures cheapness, Return on Invested
Capital (EBIT/invested capital) measures quality. Rank all stocks by each,
add ranks, buy the top 30. Reported 30.8% annualized 1988-2004.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def magic_formula(ticker):
    """Compute Earnings Yield and ROIC for a single stock."""
    stock = yf.Ticker(ticker)
    inc = stock.income_stmt
    bs = stock.balance_sheet
    info = stock.info

    ebit = float(inc.loc['EBIT'].iloc[0]) if 'EBIT' in inc.index else None
    market_cap = info.get('marketCap', None)
    total_debt = float(bs.loc['Total Debt'].iloc[0]) if 'Total Debt' in bs.index else 0
    cash = float(bs.loc['Cash And Cash Equivalents'].iloc[0]) if 'Cash And Cash Equivalents' in bs.index else 0
    ev = (market_cap + total_debt - cash) if market_cap else None

    ppe = float(bs.loc['Net PPE'].iloc[0]) if 'Net PPE' in bs.index else 0
    nwc_assets = float(bs.loc['Current Assets'].iloc[0]) if 'Current Assets' in bs.index else 0
    nwc_liab = float(bs.loc['Current Liabilities'].iloc[0]) if 'Current Liabilities' in bs.index else 0
    invested_capital = ppe + (nwc_assets - nwc_liab)

    ey = (ebit / ev * 100) if ebit and ev and ev > 0 else None
    roic = (ebit / invested_capital * 100) if ebit and invested_capital and invested_capital > 0 else None

    return {'earnings_yield': ey, 'roic': roic}

if __name__ == "__main__":
    tickers = ['AAPL','MSFT','GOOG','AMZN','META','NVDA','JPM','V','JNJ',
               'WMT','PG','MA','HD','CSCO','PM','MRK','UNH','ACN','BLK',
               'ITW','NEE','APD','BA','F','INTC','GM','XOM','CVX','CAT',
               'CL','KO','PEP','ABT','TXN','QCOM','IBM','VZ','WFC','GS',
               'LMT','HON','UPS','DE','LOW','COST','NKE','MCD','CRM','ADBE']
    results = {}
    for tk in tickers:
        try:
            results[tk] = magic_formula(tk)
            ey = results[tk]['earnings_yield']
            roic = results[tk]['roic']
            print(f"  {tk}: EY={ey:.1f}% ROIC={roic:.1f}%" if ey and roic else f"  {tk}: incomplete data")
        except Exception as e:
            print(f"  {tk}: ERROR - {e}")

    df = pd.DataFrame(results).T.dropna()
    if len(df) > 0:
        df['ey_rank'] = df['earnings_yield'].rank(ascending=False)
        df['roic_rank'] = df['roic'].rank(ascending=False)
        df['magic_rank'] = df['ey_rank'] + df['roic_rank']
        df = df.sort_values('magic_rank')

        fig, ax = plt.subplots(figsize=(10, 7))
        colors = ['#2ecc71' if r <= 10 else '#e74c3c' if r > len(df)-5 else '#3498db'
                  for r in range(1, len(df)+1)]
        ax.scatter(df['earnings_yield'], df['roic'], c=colors, s=60, alpha=0.7)
        for tk in list(df.index[:5]) + list(df.index[-5:]):
            ax.annotate(tk, (df.loc[tk,'earnings_yield'], df.loc[tk,'roic']),
                        fontsize=8, color='darkred')
        ax.set_xlabel('Earnings Yield (%)')
        ax.set_ylabel('Return on Invested Capital (%)')
        ax.set_title('Magic Formula: Earnings Yield vs ROIC')
        plt.tight_layout()
        plt.savefig('fig_ch02_magic_formula.png', dpi=150)
        plt.show()
        print(f"\nTop 10 by Magic Formula rank:")
        print(df[['earnings_yield','roic','magic_rank']].head(10).to_string())
