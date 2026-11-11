---
description: Read what the virtual deal team (Deal lead, Forensic partner, Risk officer) filed in the last 24 hours, triage its proposals awaiting a human decision, or ask one seat one question asynchronously (asynchronous desks run under budget guards and are still in verification).
argument-hint: "<deal_id> [briefing|proposals|item <item_id>|ask <seat> \"<question>\"]"
---

# Deal Team

Use this when the user asks what the deal team has done, what is waiting on a decision, or wants a specific seat to look into something.

## Usage

```
/deal-team <deal_id>
/deal-team <deal_id> proposals
/deal-team <deal_id> item <item_id>
/deal-team <deal_id> ask risk-officer "Which customer contracts have change-of-control clauses?"
```

## Execution

1. Default or `briefing`: call `mcp__ololand__get_team_briefing(deal_id)`. `{"briefing": null}` means the deal has no team yet or the team has been quiet. Say that; do not invent activity.
2. `proposals`: call `mcp__ololand__list_team_proposals(deal_id)`. The default status is `pending,parked`; `executing` surfaces stale claims. Show what each seat wants to write, its evidence, and how that evidence resolved.
3. `item`: call `mcp__ololand__get_team_work_item(deal_id, item_id)` for the seat, instruction, status, and filed artifact.
4. `ask`: confirm the seat and question with the user first, because this reserves budget, consumes credits, and dispatches work that runs without the user present. Then call `mcp__ololand__ask_team_seat(deal_id, seat, question)`. Seats: `deal-lead-seat`, `risk-officer`, `forensic-partner`. It returns a `work_item_id`, not an answer; read the result later with step 3.

## Guardrails

- Reads decide nothing. A person accepts or rejects proposals in the OloLand app.
- `ask` is refused unless the account holds both the deal-team meetings grant and the async-desk grant. Report the refusal; do not retry or work around it.
- Leave `web_enabled` false. Web research needs human consent that this connection cannot prove (`web_consent_required`).
- The Chair routes and records; it cannot be asked.
- A filed artifact is a seat's draft with its evidence. It still needs human review, so present it as a draft. Asynchronous desks run under budget guards and are still in verification; do not describe them as reliable without supervision.
