import time
from unittest.mock import patch, MagicMock
import app.services.seo as s


def _mock_moz_response(da: int):
    resp = MagicMock()
    resp.json.return_value = {"results": [{"domain_authority": da}]}
    resp.raise_for_status = MagicMock()
    return resp


def test_moz_fallback_no_credentials(monkeypatch):
    monkeypatch.setattr(s.settings, "MOZ_ACCESS_ID", None)
    monkeypatch.setattr(s.settings, "MOZ_SECRET_KEY", None)
    assert s.moz_metrics("example.com") == {"domain_authority": 0}


def test_moz_success(monkeypatch):
    monkeypatch.setattr(s.settings, "MOZ_ACCESS_ID", "id")
    monkeypatch.setattr(s.settings, "MOZ_SECRET_KEY", "secret")
    with patch("app.services.seo.requests.post", return_value=_mock_moz_response(65)):
        result = s.moz_metrics("example.com")
    assert result == {"domain_authority": 65}


def test_moz_cache_hit(monkeypatch):
    s._cache["cached.com"] = ({"domain_authority": 30}, time.time())
    with patch("app.services.seo.requests.post") as mock_post:
        result = s.moz_metrics("cached.com")
    mock_post.assert_not_called()
    assert result["domain_authority"] == 30


def test_moz_expired_cache_refreshes(monkeypatch):
    monkeypatch.setattr(s.settings, "MOZ_ACCESS_ID", "id")
    monkeypatch.setattr(s.settings, "MOZ_SECRET_KEY", "secret")
    s._cache["old.com"] = ({"domain_authority": 5}, time.time() - s._TTL - 1)
    with patch("app.services.seo.requests.post", return_value=_mock_moz_response(80)):
        result = s.moz_metrics("old.com")
    assert result["domain_authority"] == 80


def test_moz_fallback_on_request_error(monkeypatch):
    monkeypatch.setattr(s.settings, "MOZ_ACCESS_ID", "id")
    monkeypatch.setattr(s.settings, "MOZ_SECRET_KEY", "secret")
    with patch("app.services.seo.requests.post", side_effect=Exception("timeout")):
        assert s.moz_metrics("fail.com") == {"domain_authority": 0}
