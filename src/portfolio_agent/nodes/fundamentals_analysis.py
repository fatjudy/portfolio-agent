import json
from typing import Literal

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

load_dotenv()

class FundamentalsView(BaseModel):
    summary: str = Field(description="2-4 sentence plain-English summary of the "
                                     "company's financial health and price momentum")
    lean: Literal["bullish", "neutral", "bearish"] = Field(
        description="Overall lean based ONLY on the provided data")
    key_points: list[str] = Field(description="3-5 observations that drove the lean")

SYSTEM_PROMPT = """You are a fundamentals analyst.
You receive a data bundle for one stock: valuation & fundamentals metrics,
price momentum (SMA/RSI), and recent news headlines.

Your job:
- Summarize the company's financial health and price trend in plain English.
- Give an overall lean: bullish, neutral, or bearish.
- List the key points that drove your lean.

Rules:
- Base everything ONLY on the data provided. Do NOT invent numbers or facts.
- If important data is missing, say so instead of guessing.
- Be concise and concrete; cite the numbers you rely on."""

# 3. LLM CLIENT — Claude, told to return our typed model
_llm = ChatAnthropic(
    model="claude-sonnet-5",
).with_structured_output(FundamentalsView, method="json_schema")

# 4. helper — turn the data dict into readable text for the prompt
def _format_bundle(market_data: dict) -> str:
    return json.dumps(market_data, indent=2, default=str)

# 5. THE AGENT
def analyze_fundamentals(market_data: dict) -> FundamentalsView:
    user_content = (
        f"Analyze this stock data for {market_data['ticker']}:\n\n"
        f"{_format_bundle(market_data)}"
    )
    return _llm.invoke([
        ("system", SYSTEM_PROMPT),
        ("human", user_content),
    ])

# 6. quick manual test
if __name__ == "__main__":
    from portfolio_agent.tools.market_data import get_market_data

    data = get_market_data("AAPL")
    view = analyze_fundamentals(data)

    print("LEAN:", view.lean)
    print("\nSUMMARY:", view.summary)
    print("\nKEY POINTS:")
    for p in view.key_points:
        print(" -", p)