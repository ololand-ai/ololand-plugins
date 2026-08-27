---
description: Ask a question about a deal and get a conversational, voice-optimized response — concise answers with rounded numbers and clear recommendations.
---

# Talk to Your Deal

Have a natural conversation about a deal. Returns voice-optimized responses suitable for hands-free review, Claude Dispatch, or quick deal check-ins.

## Usage

```
/talk-to-deal <deal_id> <question>
```

## Arguments

- `deal_id` (required) — The deal to ask about.
- `question` (required) — Natural language question about the deal.

## Execution

1. Classify the request before choosing a rail:
   - For a simple, single-part voice question, call `talk_to_deal` from the MCP server with the deal_id and question.
   - For a multi-part question, an audit/review, or a question that asks for a recommendation, call `ask_deal_agent` with the user's verbatim question and this bounded list: `required_sections=["answer", "evidence", "assumptions", "open_questions"]`. Do not ask the agent to create a deal, launch analysis, or make a write merely to answer an audit/review request. If a pre-upgrade server rejects `required_sections` as an unknown argument, retry once without that argument after prepending this literal checklist: `Return exactly these Markdown H2 headings once each: ## Answer, ## Evidence, ## Assumptions, ## Open Questions.` State that the server-side completion control was unavailable; never infer a passing `completion_contract` from the fallback.
2. When using `ask_deal_agent`, inspect and relay its returned `boundary_gate`, `completion_contract`, and `grader_passed` fields. A response is not a completed or verified answer merely because text was returned. If any required field is absent, unavailable, or failed, say so plainly and do not replace it with an inferred pass.
3. Every deal fact, figure, date, risk, or recommendation must retain its returned inline source citation. Voice style may round a cited number (for example, "about $160 million [3]"), but must not remove its citation or convert missing evidence into an estimate. State unavailable evidence and the resulting limitation instead.
4. Do not state a buyer's or acquirer's identity, strategy, mandate, interest, expected synergies, or likely action unless it is supported by a tenant-authorized returned source citation. A caller-supplied premise may be discussed only when labeled as a hypothetical, not as a fact about the buyer.
5. The response uses voice-mode directives:
   - Concise (2-3 sentences per point)
   - Rounded numbers ("about 160 million" not "$164,501,234")
   - Narrative style, no markdown tables
   - Clear recommendation or next question at the end

## Examples

- `/talk-to-deal deal123 What are the top three risks?`
- `/talk-to-deal deal123 Is this a good deal at 8x EBITDA?`
- `/talk-to-deal deal123 Summarize the financials in 30 seconds`
- `/talk-to-deal deal123 What did we learn from similar deals?`
- `/talk-to-deal deal123 What's the risk-adjusted IRR?`

## Use Cases

- **Morning deal check**: Quick verbal summary of overnight analysis results
- **Commute review**: Hands-free deal assessment via Claude Dispatch
- **IC prep**: Rapid-fire Q&A to prepare for investment committee
- **Telegram/Discord**: Quick deal updates via Claude Channels
