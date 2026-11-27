# TLT Bonus Outperformance Certificate

This project values the iShares 20+ Year Treasury Bond ETF (TLT) Bonus Outperformance Certificate (ISIN CH1506044580) using a simplified benchmark model. It compares the non-callable value with the callable value to estimate the value of the issuer’s early-redemption right.

## Method

- TLT is modelled under the risk-neutral measure using geometric Brownian motion with constant volatility, interest rate and continuous distribution yield.
- The non-callable certificate is valued using Monte Carlo simulation and a CRR binomial tree.
- The callable certificate is valued using the same tree. On each remaining call observation date, the node value is the lower of the continuation value and the discounted early-redemption payment.
- The valuation uses Actual/365 Fixed year fractions and places contractual call observation dates exactly on the tree grid.

## Project structure

| File | Purpose |
|---|---|
| `certificate.py` | Contract terms and call schedule |
| `market_data.py` | Dated market inputs and time calculations |
| `payoff.py` | Maturity payoff function |
| `models.py` | GBM simulation and CRR tree helpers |
| `pricing.py` | Monte Carlo, non-callable tree and callable tree valuation |
| `test_benchmark_01.py` | Runs valuations and convergence checks |

## Usage

1. Set `valuation_date`, `spot_price`, `SOFR`, `volatility` and `distribution_yield` in `market_data.py`.
2. Use the unadjusted TLT close for `spot_price`.
3. Run `test_benchmark_01.py` to obtain the non-callable value, callable value and issuer call-right value.

## Limitations

- The model excludes issuer credit risk, transaction costs and bid–ask effects.
- It uses historical volatility, a flat SOFR-derived rate and a continuous distribution-yield approximation.
- Tree values fluctuate with resolution because the payoff is discontinuous at the barrier.
- The results are benchmark estimates, not exact market prices.