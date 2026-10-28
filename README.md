# Paper Screens

Python examples of fundamental stock screens inspired by academic research. The repository includes ten screening examples and a signal-parity example that combines price and fundamental signals.

## Getting started

```sh
git clone https://github.com/hakvinv/paper-screens.git
cd paper-screens
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ch01_piotroski_fscore.py
```

The scripts fetch financial data from Yahoo Finance and require an internet connection. They are simplified examples; data availability and implementation choices affect their output.

## Examples

| File | Topic |
| --- | --- |
| `ch01_piotroski_fscore.py` | Piotroski F-score |
| `ch02_magic_formula.py` | Magic Formula |
| `ch03_altman_zscore.py` | Altman Z-score |
| `ch04_gross_profitability.py` | Gross profitability |
| `ch05_sloan_accruals.py` | Accruals |
| `ch06_beneish_mscore.py` | Beneish M-score |
| `ch07_graham_netnet.py` | Net-net stocks |
| `ch08_cashflow_vs_netincome.py` | Cash flow and net income |
| `ch09_dividend_aristocrats.py` | Dividend stocks |
| `ch10_composite_score.py` | Composite score |
| `ch11_signal_parity.py` | Combined price and fundamental signals |

The scripts are companion material for *Paper Screens: 10 Fundamental Screens Exposed* by Hakvin Vosteen.
