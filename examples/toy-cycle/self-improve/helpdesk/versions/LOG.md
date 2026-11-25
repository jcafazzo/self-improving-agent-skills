# Version log: helpdesk

Append-only. One row per decision. Rows are written by `sia.py` (init, promote, reject, snapshot); do not edit or delete existing rows. Scores read "all (train, holdout)". (This log is an addition, not from the video, which describes the versions folder loosely.)

| date | version | live score | candidate score | change | decision | decided-by |
|---|---|---|---|---|---|---|
| 2026-11-24 | v001 | - | - | initial scaffold from template | created | human |
| 2026-11-24 | v002 | - | - | first written version of the helpdesk generator | edited | human |
| 2026-11-24 | v003 | 6/8 (train 4/6, holdout 2/2) | 7/8 (train 5/6, holdout 2/2) | Add the discount policy (up to 10% without approval, Dana approves above 10% via #discounts, 25% cap) to What the agent knows; addresses c003. | promoted | human |
| 2026-11-24 | rejected-001 | 7/8 (train 5/6, holdout 2/2) | 7/8 (train 5/6, holdout 2/2) | Rewrite the refunds line to cover custom-printed orders (not refundable; misprints within 14 days of delivery reprinted or refunded); addresses c005. | rejected: fixes c005 but regresses c002: the rewrite dropped the 30-day standard refund window | human |
