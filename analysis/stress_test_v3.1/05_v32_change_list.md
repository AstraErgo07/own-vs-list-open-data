# Proposed v3.2 change list

Kept separate from the v3.1 results. Each item: old value, new value,
reason. No silent edits to v3.1 defaults. Main stays on v3.1. These
changes go on branch `v3.2`.

1. **Marketplace labels.**
   - Old: "A · Entrant (Joybuy-like)", "B · Established (Amazon UK-like)".
   - New: "A · Entrant", "B · Established". A clear note: A is
     Joybuy-inspired and illustrative, not Joybuy's actual economics.
     Real names (Joybuy, JD, Amazon, Currys, THG, Zalando) appear only
     where a published figure is cited. No invented brand names.
   - Reason: the user asked about fictitious names. Generic letters
     keep the model from being read as Joybuy's books, while real
     names on citations keep the sourcing honest.

2. **Honesty wording on "not fitted".**
   - Old: "the model was not fitted to Joybuy's launch."
   - New: "Parameters were not searched to hit a 100% 1P mix. The
     0% seller-coverage default was set to the launch-day 1P-only
     state, which is published, and that choice does most of the
     work on the unit 100% 1P result. 0% remains the evidenced
     launch value; it is an Assumption for later dates (see Task 0)."
   - Reason: Task 7. The default coverage is not changed.

3. **Do not change these defaults** (logged as no-change, with reason):
   - Seller coverage 0% / 90%: Task 0 gives no published non-zero
     replacement. The 0–10% range is a sensitivity, not a new default.
   - Haircut 5%: still inside the pre-committed 0–10% band; 25% remains
     a stress test. No new measurement.
   - Spillover 8%, variable share 70%, strategic threshold 50%,
     introductory commission 7%, established ad take 3%: no new
     published figure. The 50% threshold should be labelled more
     clearly as an Assumption with no citation.
   - Do not tune B toward Amazon's 39% implied 1P unit share.

4. **Reviewer warning on the THG / Zalando proxies** (documentation,
   not a default change).
   - Old: B mid-band 5 Bring, 25% of sub-categories, 6% of modelled
     sales, presented as the established result.
   - New: the same default numbers, with a prominent note that a
     5-point cut in those established gross margins removes all five
     B 1P lines. The 25%/6% headline is assumption-driven.
   - Reason: Task 5b.

5. **Task 6 (price bands, SKU curves, grocery / toys / home and
   garden)** is implemented as v3.2 exploratory analysis, not folded
   into the v3.1 mid-band tables. Every new proxy is cited or labelled
   UNVERIFIED.
