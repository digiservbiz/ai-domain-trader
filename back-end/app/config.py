import os
from dotenv import load_dotenv
load_dotenv()
class Settings:
    OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
    GODADDY_KEY      = os.getenv("GODADDY_KEY")
    GODADDY_SECRET   = os.getenv("GODADDY_SECRET")
    DATABASE_URL     = os.getenv("DATABASE_URL")
    REDIS_URL        = os.getenv("REDIS_URL")
    MOZ_ACCESS_ID    = os.getenv("MOZ_ACCESS_ID")
    MOZ_SECRET_KEY   = os.getenv("MOZ_SECRET_KEY")
settings = Settings()
