"""
Chapter 7: Graham Net-Net
Graham, 'Security Analysis', McGraw-Hill, 1934.

NCAV = Current Assets - Total Liabilities
Buy when market cap < (2/3) * NCAV. This is Graham's most conservative
screen: buying assets at a discount to liquidation value.

Net-nets are nearly extinct in the US market. In 2025, you can find
perhaps 10-20, almost all micro-caps below $50M market cap.
"""
import yfinance as yf
import pandas as pd
import numpy as np

def graham_netnet(ticker):
    """Compute NCAV and net-net ratio for a single stock."""
    stock = yf.Ticker(ticker)
    bs = stock.balance_sheet
    info = stock.info

    ca = float(bs.loc['Current Assets'].iloc[0]) if 'Current Assets' in bs.index else None
    tl = float(bs.loc['Total Liabilities Net Minority Interest'].iloc[0]) if 'Total Liabilities Net Minority Interest' in bs.index else None
    market_cap = info.get('marketCap', None)

    if all(v is not None for v in [ca, tl, market_cap]) and market_cap > 0:
        ncav = ca - tl
        ratio = market_cap / ncav if ncav > 0 else float('inf')
        return {'ncav': ncav, 'market_cap': market_cap, 'ratio': ratio,
                'is_netnet': ratio < 2/3 if ncav > 0 else False}
    return None

if __name__ == "__main__":
    tickers = ['AAPL','MSFT','GOOG','AMZN','META','NVDA','JPM','V','JNJ',
               'WMT','PG','MA','HD','CSCO','MRK','UNH','ACN','BA','F',
               'INTC','GM','XOM','CVX','CAT','CL','KO','PEP','ABT','TXN',
               'QCOM','IBM','VZ','WFC','GS','LMT','HON','DE','LOW','COST']
    results = {}
    for tk in tickers:
        try:
            r = graham_netnet(tk)
            if r:
                results[tk] = r
                ncav_b = r['ncav'] / 1e9
                mcap_b = r['market_cap'] / 1e9
                flag = "*** NET-NET ***" if r['is_netnet'] else ""
                print(f"  {tk}: NCAV=${ncav_b:.1f}B  MCap=${mcap_b:.1f}B  Ratio={r['ratio']:.1f}x {flag}")
        except Exception as e:
            print(f"  {tk}: ERROR - {e}")

    print("\nNote: Net-nets are nearly extinct among large-cap stocks.")
    print("The screen is most relevant for micro-caps and international markets.")
