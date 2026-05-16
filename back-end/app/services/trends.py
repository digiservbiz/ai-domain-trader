import time
import logging
from pytrends.request import TrendReq

logger = logging.getLogger(__name__)

_cache: dict[str, tuple[int, float]] = {}
_TTL = 3600  # 1 hour


def gscore(keyword: str) -> int:
    """Return Google Trends interest score (0-100) for a keyword."""
    now = time.time()
    if keyword in _cache:
        score, ts = _cache[keyword]
        if now - ts < _TTL:
            return score

    try:
        pt = TrendReq(hl="en-US", tz=0, timeout=(10, 25))
        pt.build_payload([keyword], timeframe="today 3-m")
        df = pt.interest_over_time()
        if df.empty or keyword not in df.columns:
            score = 0
        else:
            score = int(df[keyword].iloc[-1])
    except Exception as exc:
        logger.warning("Google Trends lookup failed for %r: %s", keyword, exc)
        score = 0

    _cache[keyword] = (score, now)
    return score
