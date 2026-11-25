# Coach brief: run 002 (candidate.md)

Written by sia.py record. Train rows only; holdout rows are withheld from the coach.

Train score: 5 of 6 matched.

## Misses

### c005
- Input: A customer wants to return a custom-printed wedding notebook. Can we refund it?
- Expected: No. Custom-printed orders are not refundable. If it was misprinted, we reprint or refund it if they report it within 14 days of delivery.
- Must include: custom-printed orders not refundable; misprint exception; 14 days from delivery
- Agent's answer: Standard items can be refunded within 30 days of delivery, but my instructions do not say whether custom-printed items are treated differently. Check with whoever handles refunds before promising anything.
- Verifier's reason: Still does not say custom-printed orders are not refundable; no misprint exception or 14-day limit.

## Passes

- c001: Gives the live link, the Notion page Sales > Links, and says not to use the staging link.
- c002: States 30 days, counted from delivery.
- c003: Has all four items: 10% without approval, Dana above 10%, #discounts, 25% cap.
- c004: Forwards to wholesale@fernhill.example and says not to quote prices.
- c006: States 2pm, weekdays only, and next business day for later orders.
