# portfolio-agent

A multi-agent investment analysis system. Given a watchlist of stock tickers, it
gathers **facts** (fundamentals, news, history) and **crowd sentiment**, makes a
**fact-based Buy/Hold/Sell decision**, has an adversarial **Critic** challenge it,
then produces a signed-off report — one memo per ticker.

> ⚠️ Decision-support only. **Not financial advice.** The system recommends; a human
> approves. It never executes trades.

## Architecture

```
tickers
   │
[Controller]  ← code/graph runtime: dispatch workers, hold state, route
   │            (LLM only if routing must ever be dynamic)
   ├─→ [News tool ∥ Financials tool ∥ Sentiment node]   (tools, not agents)
   │            └──────────┬──────────┘
   │                 central state (blackboard)
   ▼
[Portfolio Manager]  ← grading matrix decides Buy/Hold/Sell (deterministic,
   ▼                   quant-driven + sentiment as modifier); LLM writes the "why"
[Critic 🤖]          ← fact-check + fact-vs-sentiment divergence  ←─┐ REJECT & loops<MAX
   │                                                                 │
   ├─ APPROVED / REJECTED(final) ────────────────────────────────────┘
   ▼
[Financial Writer 🤖]  ← writes the report + reasoning breakdown
   ▼
[Human Gate]  ← you sign off (LangGraph interrupt)
   ▼
Structured report per ticker  (APPROVED / REJECTED / LOW-CONVICTION)
```

### Who is / isn't an agent
- **Agents (LLM reasoners):** Portfolio Manager (writes reasoning), Critic, Financial Writer.
- **Deterministic:** Controller (graph runtime), data tools, validation, grading matrix, report compilation.
- **Human:** the sign-off gate.

### Coordination
Shared-state **blackboard** for information + **explicit LangGraph edges** for control,
with one bounded **reflection loop** (Critic → Portfolio Manager) and a **human gate**.

## Key design principles
1. **Facts decide, sentiment challenges.** The decision is quant-driven; sentiment is a
   modifier/cap, and the Critic uses it to detect divergence (crowded trades, hype).
2. **Deterministic where possible.** Data fetching and the Buy/Hold/Sell grading matrix
   are code, not LLM calls — auditable and reproducible. LLMs only where judgment is needed.
3. **Nothing dropped.** Rejected and low-conviction tickers get memos too.
4. **Human in the loop.** No recommendation reaches you without sign-off.

## Milestones
- **M0** Project setup ← *current*
- **M1** Deterministic data layer (collector + validation + cache)
- **M2** Sentiment node (Finnhub + Reddit + fusion)
- **M3** Graph skeleton (state, schemas, wiring — stubbed)
- **M4** Portfolio Manager (grading matrix + reasoning writer)
- **M5** Critic + reflection loop
- **M6** Report compilation + Financial Writer
- **M7** Human gate + delivery
- **M8** Evaluation + scale to watchlist

## Status
M0 — scaffold only. No logic implemented yet.
