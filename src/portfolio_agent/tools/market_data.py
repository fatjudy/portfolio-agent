"""Collector — fetches facts for one ticker and returns a single dict.
Sources: Finnhub (fundamentals + news) + Twelve Data (price history)."""

import os
from datetime import date, timedelta

import httpx
from dotenv import load_dotenv

load_dotenv()
FINNHUB_KEY = os.environ["FINNHUB_API_KEY"]
TWELVEDATA_KEY = os.environ["TWELVEDATA_API_KEY"]


# --------------------------------------------------------------------------
# 1. FETCH helpers — each just calls one API and returns the raw piece
# --------------------------------------------------------------------------
def _fetch_finnhub_metric(ticker):
    try:
        r = httpx.get("https://finnhub.io/api/v1/stock/metric",
                      params={"symbol": ticker, "metric": "all", "token": FINNHUB_KEY},
                      timeout=10)
        r.raise_for_status()                 # turn HTTP 429/500 into an exception
        return r.json().get("metric", {})    # .get -> {} if key missing
    except Exception as e:
        print(f"[warn] finnhub metric failed for {ticker}: {e}")
        return {}


def _fetch_twelvedata_closes(ticker):
    try:
        r = httpx.get("https://api.twelvedata.com/time_series",
                      params={"symbol": ticker, "interval": "1day",
                              "outputsize": 250, "apikey": TWELVEDATA_KEY},
                      timeout=10)
        r.raise_for_status()
        values = r.json().get("values", [])          # [] if key missing
        return [float(v["close"]) for v in values]
    except Exception as e:
        print(f"[warn] twelvedata series failed for {ticker}: {e}")
        return []                                     # empty -> momentum becomes None


def _fetch_news(ticker, days=14, limit=5):
    try:
        today = date.today()
        start = today - timedelta(days=days)
        r = httpx.get("https://finnhub.io/api/v1/company-news",
                      params={"symbol": ticker, "from": start.isoformat(),
                              "to": today.isoformat(), "token": FINNHUB_KEY},
                      timeout=10)
        r.raise_for_status()
        articles = r.json()
        return [{"title": a["headline"], "publisher": a["source"], "link": a["url"]}
                for a in articles[:limit]]
    except Exception as e:
        print(f"[warn] finnhub news failed for {ticker}: {e}")
        return []


# --------------------------------------------------------------------------
# 2. COMPUTE helpers — momentum numbers that aren't in any single field
# --------------------------------------------------------------------------
def _sma(closes, n):
    """Simple moving average of the last n closes (closes are newest-first)."""
    if len(closes) < n:
        return None
    return sum(closes[:n]) / n


def _rsi(closes, period=14):
    """Simple 14-day RSI. closes are newest-first, so reverse to chronological."""
    prices = closes[::-1]                       # oldest -> newest
    if len(prices) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# --------------------------------------------------------------------------
# 3. ASSEMBLER — the one function the rest of the system calls
# --------------------------------------------------------------------------
def get_market_data(ticker):
    metric = _fetch_finnhub_metric(ticker)
    closes = _fetch_twelvedata_closes(ticker)
    news = _fetch_news(ticker)

    momentum = {
        "current_price": closes[0] if closes else None,
        "sma_50":  _sma(closes, 50),
        "sma_200": _sma(closes, 200),
        "rsi_14":  _rsi(closes, 14),
    }

    missing = []                               # track what came back empty
    if not metric: missing.append("fundamentals")
    if not closes: missing.append("momentum")
    if not news:   missing.append("news")

    return {
        "ticker": ticker,
        "fundamentals": metric,
        "momentum": momentum,
        "news": news,
        "meta": {
            "source": "finnhub+twelvedata",
            "fetched_ok": len(missing) == 0,   # True if everything arrived
            "missing": missing,                # e.g. ["news"]
        },
    }


# --------------------------------------------------------------------------
# 4. quick manual test (run: python -m portfolio_agent.tools.market_data)
# --------------------------------------------------------------------------
if __name__ == "__main__":
    data = get_market_data("AAPL")
    print("momentum:", data["momentum"])
    print("news[0]:", data["news"][0] if data["news"] else "none")
    print("PE (from bundle):", data["fundamentals"].get("peTTM"))