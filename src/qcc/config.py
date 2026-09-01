import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./qcc.db"
    SECRET_KEY: str = "your-secret-key-change-this"
    OPENAI_API_KEY: str = ""
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Gemini keys – each optional, loaded from environment
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
        # fallback to single GEMINI_API_KEY if present (read directly from os)
        if not keys:
            single = os.getenv("GEMINI_API_KEY")
            if single:
                keys.append(single)
        return keys

settings = Settings()

def get_settings():
    return settings
