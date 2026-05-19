import os
from dotenv import load_dotenv
load_dotenv()
class Settings:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL   = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    GODADDY_KEY        = os.getenv("GODADDY_KEY")
    GODADDY_SECRET     = os.getenv("GODADDY_SECRET")
    DATABASE_URL       = os.getenv("DATABASE_URL")
    REDIS_URL          = os.getenv("REDIS_URL")
    MOZ_ACCESS_ID      = os.getenv("MOZ_ACCESS_ID")
    MOZ_SECRET_KEY     = os.getenv("MOZ_SECRET_KEY")
    SECRET_KEY                 = os.getenv("SECRET_KEY", "change-me-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
settings = Settings()
