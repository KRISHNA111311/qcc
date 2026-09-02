import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List, Optional

# Force .env to be loaded into os.environ
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./qcc.db"
    SECRET_KEY: str = "your-secret-key-change-this"
    OPENAI_API_KEY: str = ""
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Gemini keys – will be populated from .env
    gemini_api_key1: Optional[str] = None
    gemini_api_key2: Optional[str] = None
    gemini_api_key3: Optional[str] = None
    gemini_api_key4: Optional[str] = None
    gemini_api_key5: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"   # ignore any unexpected env vars

    @property
    def GEMINI_API_KEYS(self) -> List[str]:
        keys = []
        for i in range(1, 6):
            key = getattr(self, f"gemini_api_key{i}")
            if key:
                keys.append(key)
        # Also try fallback to GEMINI_API_KEY (if present)
        if not keys:
            fallback = os.getenv("GEMINI_API_KEY")
            if fallback:
                keys.append(fallback)
        # Log which keys were found
        if keys:
            print(f"[CONFIG] Loaded {len(keys)} Gemini API key(s): {[k[:8]+'...' for k in keys]}")
        else:
            print("[CONFIG] WARNING: No Gemini API keys found!")
        return keys

settings = Settings()

def get_settings():
    return settings
