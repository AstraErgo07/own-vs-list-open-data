# Prediction score

Predictions were written to `00_predictions.md` at 05:18 UTC on 13 November
2026, before Task 0 was written up and before any new model run. Folder
later renamed to stress_test. Scoring: HIT = 1, PARTIAL = 0.5, MISS = 0.

| # | Claim | Result | Score |
|---|-------|--------|-------|
| 1 | Durables A-to-B flips (Bring to Keep) survive most one-at-a-time moves | At B, compact / peripherals / office / pushchairs / car seats stay Keep across ±5pp fulfilment and most of the coverage range. Laundry, refrigeration, laptops, tablets and cooking move Keep to Test at the edges (coverage about 57–65%, or fulfilment about −4.6 to −4.8pp) but do not become a stable Bring. | HIT |
| 2 | Outerwear, footwear and baby clothing (B Test) are fragile (no verdict > 60%) | Monte Carlo, 10,000 draws, ranges in `monte_carlo_ranges.csv`: Outerwear Bring 73.9%, Footwear Bring 64.4%, Baby clothing Bring 77.4%. None is fragile by the 60% rule. The default Test sits off the centre of the range. | MISS |
| 3 | Everyday clothing and sportswear may also be fragile | Everyday clothing max 42.3% (Bring 42.3 / Test 32.5 / Keep 25.2). Sportswear max 52.3%. Both fragile. | HIT |
| 4 | Operating 100% 1P at A holds while coverage is below 50% | It holds until coverage 72.3% at the default 8% spillover (and until 56.4% at 0% spillover), so it holds below 50%. | HIT |
| 5 | Unit 100% 1P at A breaks around 80% coverage at 8% spillover | Exact: 72.3%, first line Pushchairs, operating and unit together (above the 50% strategic threshold, so they coincide). | PARTIAL |
| 6 | At 0% spillover, unit break around 65–75% coverage | Exact: 56.4%. | PARTIAL |
| 7 | Inside 0–30% coverage, A stays 100% 1P on both layers | Holds. Evidence range is 0–10%; even at 50% and 8% spillover the mid-band is still 20/20. | HIT |
| 8 | First unit haircut break between 10% and 15% | Pushchairs unit flips to Do not range at a 13.52% haircut. Peripherals, office, car seats at 14.87%. | HIT |
| 9 | At 25% haircut, 10 of 20 mid-band unit Bring | Confirmed (the ten high-GM beauty and fashion lines). Operating stays 20/20. | HIT |
| 10 | Monte Carlo at A, operating: almost nothing fragile | 10,000/10,000 draws are 20/20 Bring. Zero fragile. Ranges: coverage 0–10%, spillover 0–20%, haircut 0–25%, variable share 50–90%, intro 5–15%, ad take 0–5%, hurdle 10–35%, fulfilment ±5pp. | HIT |
| 11 | A unit: beauty and clothing above 60%; durables closer | Beauty and baby care 100% Bring. Clothing 99.96–99.97%. Durables 58.6–67.6%. Pushchairs 58.62% is the only A fragile. | HIT |
| 12 | B beauty Bring stays above 60% | 95.3–95.8% Bring. | HIT |
| 13 | B electronics Keep stays above 60% | Compact, peripherals, office, pushchairs, car seats 90–91%. Laundry, refrigeration, laptops, tablets 60.29%. Cooking 62.2%. The 60.29% lines sit on the brief's knife-edge. | PARTIAL |
| 14 | None of the 15 flips is driven by the 25% hurdle alone | Confirmed. `hurdle_driven` is False for every sub-category. B's recommendation with hurdle 0 is unchanged. | HIT |
| 15 | The 15 flips are contribution-versus-take | Primary cause for all 15: availability-adjusted payoffs. Mid-tail and strategic isolations do not undo them. | HIT |
| 16 | B is 1P-light versus Amazon's worldwide unit mix; do not treat as a hard miscalibration | Written as a direction only, with a stated price-mix Assumption. Naive gap 39% units vs 5.6% modelled sales, unlike things. | HIT |
| 17 | Beauty Bring at B survives a 5-point GM cut, at risk at 10 points | Fails at 5 points: all four beauty lines and baby care go to Test as 3P first. The 25%/6% 1P headline at B is gone. | MISS |
| 18 | A operating Bring survives all of Task 5 | All 20 survive, including the combined adverse case, because the strategic layer ranges the core at 0% coverage. | HIT |
| 19 | A unit durables fail the 25% haircut and Currys minus 5 points | Confirmed. Combined adverse: only 8 unit Bring (beauty, baby care, footwear, sportswear, baby clothing). | HIT |
| 20 | 8% spillover is not required for default mid-band unit 100% 1P | At spillover 0% and default coverage 0%, still 20/20. The result is implied by 0% coverage plus a positive 1P contribution. | HIT |
| 21 | Calling 0% coverage "not fitted" needs more honest wording | The default was chosen to match the launch-day 1P-only state. Parameters were not searched to hit 100%, but the central input was chosen to match that launch. | HIT |

**Score: 16 HIT + 3 PARTIAL + 2 MISS = 17.5 / 21 (83%).**

The two misses are the ones a stress test is for: which B clothing lines are fragile (the Keep lines, not the Test lines), and that B's beauty 1P does not survive a 5-point cut on the THG proxy.
