import os
from dotenv import load_dotenv
load_dotenv()
class Settings:
    OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
    GODADDY_KEY      = os.getenv("GODADDY_KEY")
    GODADDY_SECRET   = os.getenv("GODADDY_SECRET")
    DATABASE_URL     = os.getenv("DATABASE_URL")
    REDIS_URL        = os.getenv("REDIS_URL")
settings = Settings()
