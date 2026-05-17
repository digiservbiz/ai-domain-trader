import time
import pandas as pd
from unittest.mock import patch, MagicMock
import app.services.trends as t


def _mock_pytrends(keyword: str, score: int):
    df = pd.DataFrame({keyword: [20, 40, score]})
    pt = MagicMock()
    pt.interest_over_time.return_value = df
    return pt


def test_gscore_returns_latest_value():
    with patch("app.services.trends.TrendReq", return_value=_mock_pytrends("testkw", 72)):
        assert t.gscore("testkw") == 72


def test_gscore_cache_hit():
    t._cache["cached"] = (55, time.time())
    with patch("app.services.trends.TrendReq") as mock_cls:
        score = t.gscore("cached")
    mock_cls.assert_not_called()
    assert score == 55


def test_gscore_expired_cache_refreshes():
    t._cache["old"] = (10, time.time() - t._TTL - 1)
    with patch("app.services.trends.TrendReq", return_value=_mock_pytrends("old", 88)):
        score = t.gscore("old")
    assert score == 88


def test_gscore_fallback_on_exception():
    with patch("app.services.trends.TrendReq", side_effect=Exception("network")):
        assert t.gscore("failkw") == 0


def test_gscore_empty_dataframe():
    pt = MagicMock()
    pt.interest_over_time.return_value = pd.DataFrame()
    with patch("app.services.trends.TrendReq", return_value=pt):
        assert t.gscore("empty") == 0
