from portfolio_agent.tools.market_data import _sma, _rsi


def test_sma_average():
    closes = [10, 20, 30]              # newest-first
    assert _sma(closes, 3) == 20       # (10+20+30)/3 = 20
    assert _sma(closes, 5) is None     # not enough data -> None


def test_rsi_in_range():
    # steadily rising prices (chronologically) -> only gains -> RSI = 100
    closes = list(range(30, 0, -1))    # newest-first: [30,29,...,1]
    rsi = _rsi(closes, 14)
    assert 0 <= rsi <= 100             # always in valid range
    assert rsi == 100.0                # all gains, no losses