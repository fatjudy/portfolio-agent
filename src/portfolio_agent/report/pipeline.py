"""Pipeline — run the whole system for one ticker and produce a report."""

from portfolio_agent.tools.market_data import get_market_data
from portfolio_agent.tools.sentiment import get_sentiment_data
from portfolio_agent.nodes.fundamentals_analyst import analyze_fundamentals
from portfolio_agent.nodes.sentiment_analyst import analyze_sentiment
from portfolio_agent.nodes.debate import run_debate, judge_debate


def build_report(ticker, fv, sv, transcript, decision) -> str:
    """Assemble everything into one markdown report (deterministic — no LLM)."""
    lines = [f"# Investment Report — {ticker}", ""]

    lines += [f"## Decision: {decision.action}", "", decision.rationale, "", "### Key risks"]
    lines += [f"- {r}" for r in decision.key_risks]

    lines += ["", "## Fundamentals view", f"*Lean: {fv.lean}*", "", fv.summary]
    lines += [f"- {p}" for p in fv.key_points]

    lines += ["", "## Sentiment view",
              f"*Mood: {sv.mood} (confidence: {sv.confidence})*", "", sv.summary]
    lines += [f"- {p}" for p in sv.notable_points]

    lines += ["", "## Debate"]
    for who, text in transcript:
        lines += [f"**{who.upper()}:** {text}", ""]

    lines += ["", "_Not financial advice._"]
    return "\n".join(lines)


def analyze(ticker) -> str:
    """The full pipeline: data -> analysts -> debate -> judge -> report."""
    fv = analyze_fundamentals(get_market_data(ticker))
    sv = analyze_sentiment(get_sentiment_data(ticker))
    transcript = run_debate(fv, sv, rounds=2)
    decision = judge_debate(ticker, transcript)
    return build_report(ticker, fv, sv, transcript, decision)


if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    print(analyze(ticker))