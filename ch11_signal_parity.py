"""
Chapter 11: Signal Parity -- Price x Fundamentals
The capstone chapter unifying Paper Trading (price signals) with
Paper Plus (fundamental screens).

P_i(t) = z(momentum_12) + z(momentum_3)     [price signal]
F_i(t) = z(ROIC) + z(GP/TA) + z(EY)         [fundamental signal]
U_i(t) = alpha(t) * P_i(t) + (1 - alpha(t)) * F_i(t)

Dynamic alpha (Signal Parity): alpha(t) = Var[F(t)] / (Var[P(t)] + Var[F(t)])
Trust the LESS noisy signal more. Same math as Risk Parity (Ch 11 of
Paper Trading), applied to signals instead of assets.
"""
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import zscore

def signal_parity(price_signals, fund_signals, lookback=12):
    """
    Combine price and fundamental signals using
    inverse-noise weighting (Signal Parity).

    price_signals: DataFrame, rows=months, cols=stocks
    fund_signals: DataFrame, same shape
    Returns: unified signal DataFrame
    """
    # Rolling variance of each signal type
    var_P = price_signals.rolling(lookback).var().mean(axis=1)
    var_F = fund_signals.rolling(lookback).var().mean(axis=1)

    # Dynamic alpha: trust the LESS noisy signal more
    alpha = var_F / (var_P + var_F)

    # Unified signal
    unified = pd.DataFrame(index=price_signals.index,
                           columns=price_signals.columns)
    for date in unified.index:
        a = alpha.loc[date]
        unified.loc[date] = (a * price_signals.loc[date]
                             + (1-a) * fund_signals.loc[date])

    return unified, alpha

if __name__ == "__main__":
    # Universe
    tickers = ['AAPL','MSFT','GOOG','AMZN','META','NVDA','V','JNJ',
               'WMT','MA','HD','CSCO','MRK','UNH','ACN','BA','F',
               'INTC','XOM','CVX','CAT','CL','KO','PEP','IBM','VZ',
               'GS','LMT','HON','DE','LOW','COST','NKE','MCD']

    # --- Price signals ---
    print("Downloading price data...")
    data = yf.download(tickers, start="2023-01-01", auto_adjust=True)['Close']
    if isinstance(data.columns, pd.MultiIndex):
        data = data.droplevel(0, axis=1)
    mp = data.resample('ME').last()
    mom12 = mp.pct_change(12)
    mom3 = mp.pct_change(3)
    latest = mp.index[-1]
    p_raw = pd.DataFrame({'mom12': mom12.loc[latest], 'mom3': mom3.loc[latest]}).dropna()
    p_raw['P'] = zscore(p_raw['mom12']) + zscore(p_raw['mom3'])

    # --- Fundamental signals ---
    print("Downloading fundamental data...")
    fund = {}
    for tk in tickers:
        try:
            stock = yf.Ticker(tk)
            inc, bs = stock.income_stmt, stock.balance_sheet
            info = stock.info
            ta = float(bs.loc['Total Assets'].iloc[0]) if 'Total Assets' in bs.index else None
            gp = float(inc.loc['Gross Profit'].iloc[0]) if 'Gross Profit' in inc.index else None
            ebit = float(inc.loc['EBIT'].iloc[0]) if 'EBIT' in inc.index else None
            mcap = info.get('marketCap', None)
            td = float(bs.loc['Total Debt'].iloc[0]) if 'Total Debt' in bs.index else 0
            cash = float(bs.loc['Cash And Cash Equivalents'].iloc[0]) if 'Cash And Cash Equivalents' in bs.index else 0
            ev = (mcap + td - cash) if mcap else None
            ppe = float(bs.loc['Net PPE'].iloc[0]) if 'Net PPE' in bs.index else 0
            nwc = (float(bs.loc['Current Assets'].iloc[0]) if 'Current Assets' in bs.index else 0) - (float(bs.loc['Current Liabilities'].iloc[0]) if 'Current Liabilities' in bs.index else 0)
            ic = ppe + nwc
            roic = ebit / ic * 100 if ebit and ic and ic > 0 else None
            gp_ta = gp / ta * 100 if gp and ta and ta > 0 else None
            ey = ebit / ev * 100 if ebit and ev and ev > 0 else None
            fund[tk] = {'ROIC': roic, 'GP_TA': gp_ta, 'EY': ey}
        except:
            pass

    f_raw = pd.DataFrame(fund).T.dropna()
    f_raw['F'] = zscore(f_raw['ROIC']) + zscore(f_raw['GP_TA']) + zscore(f_raw['EY'])

    # --- Combine ---
    common = p_raw.index.intersection(f_raw.index)
    P = p_raw.loc[common, 'P']
    F = f_raw.loc[common, 'F']

    # Static alpha = 0.5
    U = 0.5 * P + 0.5 * F
    rho = np.corrcoef(P, F)[0, 1]

    result = pd.DataFrame({'P': P, 'F': F, 'U': U}).sort_values('U', ascending=False)
    print(f"\nPrice-Fundamental correlation: rho = {rho:.3f}")
    print(f"\nUnified ranking (top 10 and bottom 5):")
    show = pd.concat([result.head(10), result.tail(5)])
    print(show.to_string(float_format='%.2f'))

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(result['P'], result['F'], s=40, alpha=0.7)
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)
    for tk in show.index:
        ax.annotate(tk, (result.loc[tk,'P'], result.loc[tk,'F']),
                    fontsize=7, color='darkred')
    ax.set_xlabel('Price Signal (momentum z-score)')
    ax.set_ylabel('Fundamental Signal (quality + value z-score)')
    ax.set_title(f'Price x Fundamentals: rho = {rho:.2f}')
    ax.text(0.02, 0.98, 'BUY\n(strong price + strong fundamentals)',
            transform=ax.transAxes, va='top', fontsize=8, color='green', alpha=0.5)
    ax.text(0.02, 0.02, 'AVOID\n(weak price + weak fundamentals)',
            transform=ax.transAxes, va='bottom', fontsize=8, color='red', alpha=0.5)
    plt.tight_layout()
    plt.savefig('fig_ch11_signal_parity.png', dpi=150)
    plt.show()
