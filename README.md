# Trading Backtester


## Vectorized vs. event-driven engine

I built the backtester twice: a vectorized engine (fast, whole price series at
once) and an event-driven engine (day-by-day loop with Order, Fill, Broker, and
Portfolio classes). The event-driven version was designed to reproduce the
vectorized one, so any difference between them has to be explained.

*AAPL, 2018-2024, $100k start, 5 bps costs. Benchmark: SPY buy-and-hold (13.7%/yr).
Alpha = strategy return minus benchmark return (not beta-adjusted).*

| Strategy | Engine | Sharpe | Max DD | Ann. return | Alpha | Final equity | Trades/yr |
|---|---|---|---|---|---|---|---|
| buy_hold_AAPL | vectorized | 1.010 | -38.5% | 29.9% | 16.2% | $622,031 | 0.1 |
| | event (fractional) | 1.010 | -38.5% | 29.9% | 16.2% | $622,031 | 0.1 |
| | event (whole shares) | 1.010 | -38.5% | 29.9% | 16.2% | $621,964 | 0.1 |
| mom_20 | vectorized | 1.205 | -25.8% | 24.8% | 11.1% | $468,906 | 20.2 |
| | event (fractional) | 1.203 | -25.9% | 24.8% | 11.1% | $468,873 | 20.2 |
| | event (whole shares) | 1.203 | -25.9% | 24.8% | 11.1% | $468,776 | 20.2 |
| mom_126 | vectorized | 0.805 | -38.1% | 18.9% | 5.2% | $334,375 | 6.4 |
| | event (fractional) | 0.805 | -38.1% | 18.9% | 5.2% | $334,389 | 6.4 |
| | event (whole shares) | 0.805 | -38.1% | 18.9% | 5.2% | $334,331 | 6.4 |
| mr_20_5% | vectorized | 0.172 | -39.9% | 1.5% | -12.2% | $110,672 | 6.6 |
| | event (fractional) | 0.172 | -39.9% | 1.5% | -12.2% | $110,669 | 6.6 |
| | event (whole shares) | 0.172 | -39.9% | 1.5% | -12.2% | $110,656 | 6.6 |

**Do they agree?**
- **Signals.** Streaming versions of both strategies (which only see data up to
  today) produced identical signals to the vectorized versions across all 10
  parameter sets tested, which confirms the vectorized signals have no look-ahead.
- **Zero costs.** Final equity matched to the cent, with a max daily difference
  around 1e-15 (floating-point noise).
- **5 bps costs.** Final equity differs by under 0.01% (e.g. mom_20: $468,906
  vectorized vs $468,873 event-driven), Sharpe by at most 0.002, and max drawdown
  by 0.1 percentage point. The cause is fee timing: the event engine charges the
  fee on the day of the trade, while the vectorized engine charges it the day after.

**What realism changes.** Restricting the event-driven engine to whole shares
lowers final equity by only 0.01-0.03% at $100k, but by about 0.5% for the
momentum strategies at $5k, where one share is a meaningful slice of the
account. (Mean-reversion at $5k moved +0.10%, so the effect can go either way.)

**Takeaway.** Differences between the engines (under 0.01%, or about 0.5% for a
small account with whole shares) are tiny next to differences between
strategies (mom_20 ends at ~$469k vs ~$334k for mom_126), so the strategy
conclusions don't depend on which engine produced them.

**Limitations.** Both engines fill at the close of the signal day, a slightly
optimistic convention; a next-open fill would be more conservative. Results are
for a single stock over one period.


## Key findings

- **Buy-and-hold AAPL beat every strategy on total return** (29.9%/yr vs 24.8% for
  the best strategy, mom_20). mom_20 had the best risk-adjusted result (Sharpe 1.2
  vs 1.0) and a shallower worst drawdown (-26% vs -39%), so it gave a smoother ride
  rather than a higher return.
- **Mean-reversion had a max drawdown (-39.9%) as deep as buy-and-hold's despite
  being mostly in cash**, with a Sharpe of only 0.17. Mean-reverstion's worst drawdown (-39%) which bottomed on 2020-03-23, the COVID crash low.

  Regime comparison. I ran each strategy once over 2018-2024, then sliced the daily returns into two windows and rebuilt a fresh $100k equity curve for each, so the lookback windows were already warmed up. In the 2022 bear market, mean-reversion was the only strategy that made money (+4.4%, max drawdown -15%), while buy-and-hold AAPL fell 26% and SPY fell 18%. Momentum was mixed: the 20-day version (-18%) roughly matched SPY, but the 126-day version lost 36%, whipsawed by bear-market rallies. In the 2023-24 bull run the ranking flipped. Buy-and-hold AAPL returned 40%/yr and SPY 26%/yr, both momentum versions earned about 21%/yr, and mean-reversion earned only 7.4%/yr. Trading frequency also changed with the market: mom_20 made about 29 trades in 2022 versus about 24 per year in the bull run, so choppy markets cost more in fees. These are single episodes on a single stock with a handful of parameter choices, so they illustrate regime dependence rather than prove it. I lean on return and drawdown here because Sharpe over a single year is noisy, and alpha vs. SPY looks inflated in 2022 mainly because SPY fell.