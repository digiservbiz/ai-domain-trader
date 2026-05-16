import re
import logging
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

_VALID_DOMAIN = re.compile(r'^[a-z0-9][a-z0-9\-]*\.[a-z]{2,}$')

_SYSTEM = (
    "You are a creative branding expert specialising in domain names. "
    "When asked, respond with ONLY a plain list of domain names — one per line, "
    "no numbering, no explanation, no markdown."
)


def brainstorm(keywords: list[str], niche: str, count: int = 10) -> list[str]:
    """Return up to `count` brandable domain name suggestions."""
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set — returning empty domain list")
        return []

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = (
        f"Generate {count} unique, brandable domain names for a {niche} startup. "
        f"Incorporate or riff on these keywords: {', '.join(keywords)}. "
        f"Mix TLDs (.com, .io, .ai). Keep names short (≤15 chars). "
        f"Return exactly one domain per line."
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=256,
        )
        raw = resp.choices[0].message.content or ""
    except Exception as exc:
        logger.error("OpenAI request failed: %s", exc)
        return []

    domains = []
    for line in raw.splitlines():
        name = line.strip().lower().lstrip("•-– ")
        if _VALID_DOMAIN.match(name):
            domains.append(name)

    return domains[:count]
