# Coach brief: run 004 (candidate.md)

Written by sia.py record. Train rows only; holdout rows are withheld from the coach.

Train score: 5 of 6 matched.

## Misses

### c002
- Input: What's our refund window?
- Expected: 30 days from delivery for standard items.
- Must include: 30 days; from delivery
- Agent's answer: My instructions only cover custom-printed orders: they are not refundable, except a misprint reported within 14 days of delivery. They do not give the refund window for standard items, so check with whoever handles refunds.
- Verifier's reason: Does not give the 30-day window from delivery for standard items; only the custom-order rule is stated.

## Passes

- c001: Gives the live link, the Notion page Sales > Links, and says not to use the staging link.
- c003: Has all four items: 10% without approval, Dana above 10%, #discounts, 25% cap.
- c004: Forwards to wholesale@fernhill.example and says not to quote prices.
- c005: States custom-printed orders are not refundable, the misprint exception, and the 14-day limit from delivery.
- c006: States 2pm, weekdays only, and next business day for later orders.
