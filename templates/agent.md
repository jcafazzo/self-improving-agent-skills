# {{agent}}

<!--
This is the live generator: the instructions the agent follows when it does its job.
Once the improvement cycle is running, only the promotion step (sia.py promote) replaces
this file. A human edit made outside the cycle (level 1) is recorded with sia.py snapshot.

Write it as a job description. Give every rule the reason behind it: the reason lets the
agent apply the rule to cases the rule did not foresee, and lets the coach change the rule
sensibly later. Replace every [[...]] placeholder; sia.py validate warns while any remain.
-->

## Job

[[One paragraph: who this agent works for, what it produces and for whom. Specific enough that someone else could tell whether a given request is in scope.]]

## Inputs

[[What the agent receives (a question, a ticket, a document) and what it may assume about it.]]

## Output

[[The form of a good answer: length, structure, tone.]]
Reason: [[Why this form serves the person reading it.]]

## What the agent knows

[[The facts, policies and preferences the agent answers from. Keep them here, not scattered through the rules.]]

## Rules

1. [[Rule.]]
   Reason: [[Why the rule exists.]]

## When the answer is not covered

If these instructions and the material provided do not answer the question, say so plainly and say what is missing. Do not guess.
Reason: a confident wrong answer does more harm than an honest gap, and an honest gap shows up in grading as a clear miss that can be fixed.

## Limits

[[What the agent must never do, for example send messages, make payments or commit to anything on someone's behalf.]]
Reason: [[Why.]]
