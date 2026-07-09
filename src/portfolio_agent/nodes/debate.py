"""Debate — Bull vs Bear argue over the two analyst views, then a Judge decides."""

from typing import Literal

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

load_dotenv()

# plain-text model for the debaters (they produce persuasive prose, not a schema)
_llm = ChatAnthropic(model="claude-sonnet-5")

# --------------------------------------------------------------------------
# PART A — the debate
# --------------------------------------------------------------------------
def _briefing(fundamentals_view, sentiment_view) -> str:
    """The shared context both debaters see (the two analyst outputs)."""
    return (
        f"FUNDAMENTALS (lean={fundamentals_view.lean}):\n"
        f"{fundamentals_view.summary}\n"
        f"Key points: {fundamentals_view.key_points}\n\n"
        f"SENTIMENT (mood={sentiment_view.mood}, confidence={sentiment_view.confidence}):\n"
        f"{sentiment_view.summary}\n"
        f"Notable: {sentiment_view.notable_points}"
    )

BULL_SYSTEM = """You are a BULL investor arguing the case to BUY this stock.
Use the briefing and the debate so far. Be persuasive but honest: build on real
evidence and directly rebut the Bear's points when they exist. One tight paragraph."""

BEAR_SYSTEM = """You are a BEAR investor arguing the case to AVOID or SELL this stock.
Use the briefing and the debate so far. Be persuasive but honest: raise real risks
and directly rebut the Bull's points. One tight paragraph."""

def _speak(system_prompt, briefing, transcript) -> str:
    """One debater's turn. It sees the briefing + the whole debate so far."""
    debate_so_far = "\n\n".join(f"{who.upper()}: {text}" for who, text in transcript)
    human = (f"BRIEFING:\n{briefing}\n\n"
             f"DEBATE SO FAR:\n{debate_so_far or '(nothing yet — you speak first)'}")
    return _llm.invoke([("system", system_prompt), ("human", human)]).content


def run_debate(fundamentals_view, sentiment_view, rounds=2):
    """Alternate Bull/Bear for a FIXED number of rounds. Returns the transcript."""
    briefing = _briefing(fundamentals_view, sentiment_view)
    transcript = []                              # shared memory of the argument
    for _ in range(rounds):                      # bounded -> can't loop forever
        transcript.append(("bull", _speak(BULL_SYSTEM, briefing, transcript)))
        transcript.append(("bear", _speak(BEAR_SYSTEM, briefing, transcript)))
    return transcript

# --------------------------------------------------------------------------
# PART B — the judge
# --------------------------------------------------------------------------
class Decision(BaseModel):
    action: Literal["BUY", "HOLD", "SELL"] = Field(description="final call")
    rationale: str = Field(description="what tipped the decision, weighing both sides")
    key_risks: list[str] = Field(description="main remaining risks to watch")


_judge = ChatAnthropic(model="claude-sonnet-5").with_structured_output(
    Decision, method="json_schema")

JUDGE_SYSTEM = """You are the portfolio manager. You are given a Bull vs Bear debate
about a stock. Weigh both sides fairly and issue a final decision: BUY, HOLD, or SELL.
Explain what tipped your decision and list the key remaining risks."""


def judge_debate(ticker, transcript) -> Decision:
    debate_text = "\n\n".join(f"{who.upper()}: {text}" for who, text in transcript)
    human = f"Debate about {ticker}:\n\n{debate_text}"
    return _judge.invoke([("system", JUDGE_SYSTEM), ("human", human)])

# --------------------------------------------------------------------------
# test — the WHOLE pipeline end to end
# --------------------------------------------------------------------------
if __name__ == "__main__":
    from portfolio_agent.tools.market_data import get_market_data
    from portfolio_agent.tools.sentiment import get_sentiment_data
    from portfolio_agent.nodes.fundamentals_analyst import analyze_fundamentals
    from portfolio_agent.nodes.sentiment_analyst import analyze_sentiment

    ticker = "AAPL"
    fv = analyze_fundamentals(get_market_data(ticker))
    sv = analyze_sentiment(get_sentiment_data(ticker))

    transcript = run_debate(fv, sv, rounds=2)
    for who, text in transcript:
        print(f"\n=== {who.upper()} ===\n{text}")

    decision = judge_debate(ticker, transcript)
    print("\n\n### DECISION:", decision.action)
    print("Rationale:", decision.rationale)
    print("Key risks:", decision.key_risks)