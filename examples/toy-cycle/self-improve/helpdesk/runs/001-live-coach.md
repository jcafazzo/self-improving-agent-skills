# Coach brief: run 001 (agent.md)

Written by sia.py record. Train rows only; holdout rows are withheld from the coach.

Train score: 4 of 6 matched.

## Misses

### c003
- Input: Who approves discounts?
- Expected: Any sales rep can apply up to 10%. Anything above 10% needs approval from Dana (Head of Sales) in #discounts. Nothing above 25%.
- Must include: up to 10% without approval; above 10% needs Dana; ask in #discounts; 25% maximum
- Agent's answer: My instructions do not cover who approves discounts. Your sales lead is the most likely person to know. I cannot apply discounts myself.
- Verifier's reason: Honestly says it is not covered, but the key has an answer: missing the 10% threshold, Dana's approval above 10%, the #discounts channel and the 25% cap.

### c005
- Input: A customer wants to return a custom-printed wedding notebook. Can we refund it?
- Expected: No. Custom-printed orders are not refundable. If it was misprinted, we reprint or refund it if they report it within 14 days of delivery.
- Must include: custom-printed orders not refundable; misprint exception; 14 days from delivery
- Agent's answer: Standard items can be refunded within 30 days of delivery, but my instructions do not say whether custom-printed items count as standard. Check with whoever handles refunds before promising anything.
- Verifier's reason: Does not say custom-printed orders are not refundable, and has no misprint exception or 14-day limit.

## Passes

- c001: Gives the live link, the Notion page Sales > Links, and says not to use the staging link.
- c002: States 30 days, counted from delivery.
- c004: Forwards to wholesale@fernhill.example and says not to quote prices.
- c006: States 2pm, weekdays only, and next business day for later orders.
