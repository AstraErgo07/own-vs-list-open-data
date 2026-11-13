> Folder and title renamed to 'stress test' at the user's request (13 Nov 2026). The predictions below are unchanged from the file written at 05:18 UTC on 13 Nov 2026, before any Task 0 write-up or any new model run for this review.

# Hostile-review predictions (written before any analysis was run)

Written: 13 November 2026, Asia/Calcutta, before Task 0 web checks and
before any new model runs for this review. Predictions use only the
reviewer's knowledge of v3.1 mechanics from the earlier implementation
(commit 3f428e0) and the already-reported default mid-band outcomes.
They will be scored after the results exist. They are not results.

Default mid-band outcomes already on the record (v3.1 README, not re-run
here for this file):
- Entrant A: 20 Bring in-house (unit and strategic agree), 100% of
  sub-categories and 100% of modelled sales. All-band: 55 Bring, 5
  Do not range (long-tail).
- Established B: 5 Bring (beauty four lines, baby care), 3 Test
  (outerwear, footwear, baby clothing), 12 Keep. 25% of
  sub-categories, 6% of modelled sales.
- 15 A-to-B flips: eight electronics/office/appliance lines, four
  clothing lines, pushchairs, car seats, baby clothing. Beauty and
  baby care do not flip.

## 1. Which of the 15 A-to-B flips I expect to survive sensitivity

Survive (still a flip under most one-at-a-time moves inside the stated
ranges): the eight electronics and appliance lines, plus pushchairs
and car seats (A Bring, B Keep). Reason: at B, Currys 18.3% after
fully loaded 12% fulfilment leaves about 3% contribution, which a
mature take (Amazon 7% referral grossed up to 8.4% of ex-VAT, plus
about 3% ads and a warehouse margin) beats by a wide margin. I expect
these Keep-3P verdicts at B to hold unless established fulfilment is
cut sharply, ads go to near zero, or electronics GM is raised, none
of which is the central case.

Fragile (likely to change recommendation at B inside the ranges):
outerwear, footwear, and baby clothing (A Bring, B Test). These were
already "near threshold" at B. A small move in spillover, coverage,
ad take, or clothing fulfilment will turn Test into Keep or Bring.
Everyday clothing and sportswear (A Bring, B Keep) I expect to be
close behind: Zalando 23% fulfilment uses most of the 39.9% GM, so
the 3P take only just wins. A 5-point clothing GM cut (Task 5b)
may push more clothing to Keep, and a 10-point cut may also threaten
beauty at B.

## 2. Which entrant verdicts I expect to break

The mid-band operating (strategic) 100% 1P result I expect to hold
for as long as seller coverage stays below the 50% land-grab
threshold, because the strategic layer ranges mid- and high-velocity
lines as 1P regardless of unit contribution. That 50% threshold is
itself an Assumption, and I expect it to be the binding constraint
on the *operating* mix.

The mid-band *unit* 100% 1P result I expect to break before that, or
around it, once coverage is high enough that
coverage × (entrant 3P take + spillover) exceeds 1P contribution +
spillover. Back-of-envelope, electronics contribution is about 6% of
price, entrant take about 9%, default spillover 8%: the unit flip
for durables is around coverage 80% at default spillover, and around
coverage 65–70% if spillover is 0%. Clothing and beauty unit 1P I
expect to survive the full 0–30% *entrant* coverage range in Task 1
(that range only goes to 30%, which is below both the 50% strategic
threshold and my estimated unit-flip coverage). So: inside Task 1's
stated 0–30% entrant coverage range, I predict the entrant stays
100% 1P on both layers. The combination that stops 100% 1P will only
appear if we also look above 30% coverage, which the brief requires
us to state. I predict:

- Operating 100% 1P breaks at coverage = 50% only if unit has already
  flipped at least one mid-band line; otherwise it breaks at the
  unit flip coverage (I predict about 80% at 8% spillover for the
  first electronics line).
- Unit 100% 1P at 0% spillover breaks at lower coverage (I predict
  about 65–75% for the first durable).
- At the 25% haircut stress, unit 100% 1P already fails at 0%
  coverage (previously reported: 10 of 20 mid-band unit Bring, the
  high-GM lines only). I expect that to be confirmed, and I expect
  the first unit breaks on electronics to appear between 10% and
  15% haircut because ROC on thin durables may fall through the
  25% hurdle.

I also expect Task 5b (beauty and clothing GM cut 10 points) and
Task 5c (electronics 5 points below Currys) to break some *unit*
entrant verdicts on durables if ROC fails, while the strategic
layer still ranges them as 1P at 0% coverage.

## 3. Monte Carlo: what I expect to be fragile (no verdict > 60%)

At A (entrant): almost nothing. Coverage in 0–30% keeps the
strategic layer on, so operating Bring should be well above 60%
for all 20 mid-band lines. Unit layer may be fragile for
electronics if haircut, variable-share and spillover land in the
adverse corner, but I predict even unit Bring stays above 60% for
beauty and clothing, and is closer for durables.

At B (established): outerwear, footwear, baby clothing (the Test
lines) I predict are fragile (no verdict > 60%). Everyday clothing
and sportswear may also be. Beauty I predict stays Bring above 60%.
Electronics Keep I predict stays above 60%, possibly except compact
or peripherals if GM and fulfilment draws go the other way.

Overall 1P share: at A I predict the distribution of operating 1P
sub-category share is tight around 100% (because coverage ≤ 30% in
the stated range keeps the land-grab on). At B I predict a wide
distribution, median perhaps 20–40% of sub-categories and well
below that for sales, with a long right tail if ads and coverage
draw low.

## 4. Attribution of the 15 flips

I predict none of the 15 is driven by the 25% GMROI hurdle alone.
At A, mid-band ROC was previously above the hurdle for all 20
(minimum about 36%). At B, electronics fail because contribution
loses to a mature 3P take (contribution-vs-take), not because ROC
fails a 25% bar that contribution would otherwise pass. Clothing
Test cases I predict are "near threshold" on contribution-vs-take.
Demand predictability (mid-tail) may colour baby clothing and
outerwear toward Test rather than Keep or Bring. The strategic
layer is off at B (coverage 90% ≥ 50%), so it does not cause
the B-side of any flip. Inventory liquidity is a cost inside
contribution and ROC, not a separate flip trigger.

## 5. Amazon calibration gap

B's 6% 1P modelled-sales share versus Amazon's disclosed 61% 3P
share of worldwide paid units (implying about 39% 1P by units) is
a large gap. I predict the 2–3 parameters most responsible are:
(1) applying a full Amazon-UK-like 3P take (referral plus 3% ads
plus warehouse margin) to every 3P-covered unit, which is a rich
take; (2) Currys 18.3% and Zalando 23% fulfilment, which make
durables and fashion lose on contribution; (3) the modelled
category mix itself (five categories, mid-band prices, no grocery
or media, 1P concentrated in lower-priced beauty). I predict B
is miscalibrated toward too little 1P on a sales-weighted basis,
but the comparison is not clean: Amazon's 61% is worldwide paid
*units*, excluding Whole Foods, not UK sales, and this model's
"sales" are assumed prices times assumed weekly units in only
five categories. I will convert units to sales with an explicit
price-mix assumption and will not tune.

## 6. Task 5 survivors

I predict beauty Bring at B survives a 5-point GM cut but is at
risk on a 10-point cut. Entrant operating Bring survives all of
Task 5 (strategic layer at 0% coverage). Entrant unit Bring on
durables I predict does *not* survive the 25% haircut, and may
not survive electronics at Currys minus 5 points. Baby care
follows beauty.

## 7. Task 6 (breadth)

I predict some of the original 20 mid-band verdicts are not
robust once low and high bands, a Pareto tail, and a fixed
pick/pack plus minimum referral are in play: high-price
low-velocity SKUs at A may go to Do not range (already true
for five all-band lines), and low-price SKUs at B may flip
because of the £0.25 minimum referral (take rate rises on cheap
items) or a fixed pick/pack (1P fulfilment share rises on cheap
items). I expect mid-band beauty Bring and mid-band electronics
Keep at B to survive; I expect the clothing Test lines and
possibly compact appliances not to.

## 8. Task 7 (circularity) — what I expect the audit to conclude

- 0% coverage plus spillover: the 8% spillover is *not* necessary
  for mid-band unit 100% 1P at the defaults (previously shown at
  spillover 0%). The result *is* implied by 0% coverage (the
  alternative payoff is zero) plus a positive 1P contribution.
  That is the right alternative if coverage really is 0%, but it
  is an Assumption, and calling 0% "consistent with a 1P-only
  launch" is close to building the launch into the input. I will
  call this assumption-driven, and I will say the "not fitted"
  claim is technically true of the *parameters* (they were not
  searched to hit 100%) but the coverage default was chosen to
  match the launch. That wording needs to be more honest.
- The 50% strategic threshold is arbitrary (no citation).
- The 5% haircut uses JD China 20-F supplier language; Joybuy is
  not named in the 20-F; the residual 5% is a UK-local Assumption
  dressed with a parent-company quote.
- Single-unit comparison ignores cannibalisation, buy-box and
  seller churn, as the model already discloses.

## Scoring rule (applied after results)

For each numbered claim above, mark HIT, PARTIAL, or MISS, with
the actual figure. The score is HIT + 0.5*PARTIAL, over the
number of scored claims, stated as a fraction. Predictions that
were already known from the v3.1 implementation write-up will be
labelled as such and will not be counted as fresh hits if the
new run merely repeats them.
