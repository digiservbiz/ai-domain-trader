import time
import logging
import requests
from requests.auth import HTTPBasicAuth
from app.config import settings

logger = logging.getLogger(__name__)

_cache: dict[str, tuple[dict, float]] = {}
_TTL = 3600  # 1 hour

_MOZ_URL = "https://lsapi.seomoz.com/v2/url_metrics"
_FALLBACK = {"domain_authority": 0}


def moz_metrics(domain: str) -> dict:
    """Return Moz domain authority metrics for a domain.

    Falls back to zeros when credentials are absent or the request fails.
    """
    now = time.time()
    if domain in _cache:
        data, ts = _cache[domain]
        if now - ts < _TTL:
            return data

    if not (settings.MOZ_ACCESS_ID and settings.MOZ_SECRET_KEY):
        return _FALLBACK

    try:
        resp = requests.post(
            _MOZ_URL,
            auth=HTTPBasicAuth(settings.MOZ_ACCESS_ID, settings.MOZ_SECRET_KEY),
            json={"targets": [domain]},
            timeout=10,
        )
        resp.raise_for_status()
        row = resp.json().get("results", [{}])[0]
        data = {"domain_authority": int(row.get("domain_authority", 0))}
    except Exception as exc:
        logger.warning("Moz metrics lookup failed for %r: %s", domain, exc)
        data = _FALLBACK

    _cache[domain] = (data, now)
    return data
