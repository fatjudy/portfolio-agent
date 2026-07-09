import json
from typing import Literal

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

load_dotenv()


# 1. OUTPUT SHAPE
class SentimentView(BaseModel):
    mood: Literal["euphoric", "positive", "neutral", "negative", "fearful"] = Field(
        description="Overall emotional tone of the recent news flow")
    summary: str = Field(description="2-4 sentence summary of the prevailing mood "
                                     "and what's driving it")
    notable_points: list[str] = Field(
        description="3-5 recurring themes or striking phrases from the coverage")
    confidence: Literal["low", "med", "high"] = Field(
        description="How confident, based on HOW MUCH coverage there is "
                    "(few articles -> low, lots -> high)")    

# 2. SYSTEM PROMPT
SYSTEM_PROMPT = """You are a market sentiment analyst.
You receive a batch of recent news articles (headlines + summaries) about one stock.

Your job is to read the MOOD, not the fundamentals:
- Judge the overall emotional tone of the coverage.
- Summarize what's driving that mood.
- Note recurring themes or striking language.
- Set your confidence based on HOW MUCH coverage there is.

Rules:
- Judge tone/emotion, NOT whether the company is a good investment.
- Base everything ONLY on the articles provided. Do not invent news.
- If there are very few articles, say so and set confidence to low."""

# 3. LLM CLIENT
_llm = ChatAnthropic(
    model="claude-sonnet-5",
).with_structured_output(SentimentView, method="json_schema")


# 4. formatter
def _format_bundle(sentiment_data: dict) -> str:
    return json.dumps(sentiment_data, indent=2, default=str)


# 5. THE AGENT
def analyze_sentiment(sentiment_data: dict) -> SentimentView:
    user_content = (
        f"Analyze the news sentiment for {sentiment_data['ticker']} "
        f"({sentiment_data['meta']['article_count']} articles):\n\n"
        f"{_format_bundle(sentiment_data)}"
    )
    return _llm.invoke([
        ("system", SYSTEM_PROMPT),
        ("human", user_content),
    ])


# 6. quick test
if __name__ == "__main__":
    from portfolio_agent.tools.sentiment import get_sentiment_data

    data = get_sentiment_data("AAPL")
    view = analyze_sentiment(data)

    print("MOOD:", view.mood, "| CONFIDENCE:", view.confidence)
    print("\nSUMMARY:", view.summary)
    print("\nNOTABLE POINTS:")
    for p in view.notable_points:
        print(" -", p)