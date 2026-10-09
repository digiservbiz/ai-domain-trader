import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    GODADDY_KEY = os.getenv("GODADDY_KEY")
    GODADDY_SECRET = os.getenv("GODADDY_SECRET")
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    MOZ_ACCESS_ID = os.getenv("MOZ_ACCESS_ID")
    MOZ_SECRET_KEY = os.getenv("MOZ_SECRET_KEY")
    SECRET_KEY = os.environ["SECRET_KEY"]
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
    COOKIE_SECURE = os.getenv(
        "COOKIE_SECURE",
        "true" if ENVIRONMENT == "production" else "false",
    ).strip().lower() == "true"
    TRADING_MODE = os.getenv("TRADING_MODE", "paper").strip().lower()
    LIVE_TRADING_ENABLED = os.getenv("LIVE_TRADING_ENABLED", "false").strip().lower() == "true"

    @property
    def can_place_live_bids(self) -> bool:
        """Fail closed unless both independent live-trading flags are explicit."""
        return self.TRADING_MODE == "live" and self.LIVE_TRADING_ENABLED


settings = Settings()
