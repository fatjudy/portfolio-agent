# Evaluation cases

Define "good" *before* building. Pick 5–10 historical situations where you already
know what happened, and write down what a **good** analysis would have concluded.
When the system is built (M8), we replay these and check the system's *reasoning and
risk-catching*, not just whether the final Buy/Hold/Sell matched hindsight.

## How to fill this in
For each case, use a point in time (`as_of`) and only judge the system on what was
knowable then. The key column is **"what a good analyst should have caught"** — that
is what we actually grade the Critic on.

## Case template

| # | Ticker | as_of date | Situation (1 line) | Facts said | Sentiment was | What a good analyst should have caught | Actual outcome |
|---|--------|-----------|--------------------|-----------|---------------|----------------------------------------|----------------|
| 1 |        |           |                    |           |               |                                        |                |
| 2 |        |           |                    |           |               |                                        |                |

## Categories to cover (aim for a spread)
- [ ] **Crowded trade** — strong facts + euphoric sentiment that then pulled back.
- [ ] **Hype detached from fundamentals** — weak facts + euphoric crowd (pump/bubble).
- [ ] **Divergence / early warning** — sentiment turned negative before the facts did.
- [ ] **Clean buy** — solid facts, calm sentiment, worked out.
- [ ] **Value trap** — cheap on paper but deteriorating fundamentals.
- [ ] **Thin data** — a ticker where the data layer should trigger LOW-CONVICTION.

## Grading (M8)
For each case, score:
1. **Decision** — did the grading matrix land on a reasonable action?
2. **Risk-catching** — did the Critic flag the risk in the "should have caught" column?
3. **Grounding** — were the claims tied to real datapoints (no hallucinated numbers)?
4. **Trajectory** — did the reflection loop improve the thesis, or churn?
