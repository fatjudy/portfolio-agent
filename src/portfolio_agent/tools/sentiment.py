"""Sentiment data — recent news flow for a ticker (mood signal).
News-based because Reddit is blocked behind the user's China VPN."""

import os
from datetime import date, timedelta

import httpx
from dotenv import load_dotenv

load_dotenv()
FINNHUB_KEY = os.environ["FINNHUB_API_KEY"]


def fetch_news_for_sentiment(ticker, days=7, limit=20):
    """Return recent articles (headline + summary) for mood analysis."""
    try:
        today = date.today()
        start = today - timedelta(days=days)
        r = httpx.get("https://finnhub.io/api/v1/company-news",
                      params={"symbol": ticker, "from": start.isoformat(),
                              "to": today.isoformat(), "token": FINNHUB_KEY},
                      timeout=10)
        r.raise_for_status()
        articles = r.json()
        return [{"headline": a["headline"],
                 "summary": a.get("summary", "")[:300],   # trim long bodies
                 "source": a["source"]}
                for a in articles[:limit]]
    except Exception as e:
        print(f"[warn] news fetch failed for {ticker}: {e}")
        return []


def get_sentiment_data(ticker):
    """Assemble the sentiment bundle for one ticker."""
    articles = fetch_news_for_sentiment(ticker)
    return {
        "ticker": ticker,
        "articles": articles,
        "meta": {
            "source": "finnhub-news",
            "article_count": len(articles),      # how much coverage -> confidence
            "fetched_ok": len(articles) > 0,
        },
    }


if __name__ == "__main__":
    data = get_sentiment_data("AAPL")
    print("article_count:", data["meta"]["article_count"])
    for a in data["articles"][:3]:
        print(f"\n[{a['source']}] {a['headline']}")
        print(a["summary"][:150])