from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    DB_URL: str

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    SECRET_KEY: str

    CLOUDINARY_URL: Optional[str] = None
    CLD_NAME: Optional[str] = None
    CLD_API_KEY: Optional[int] = None
    CLD_API_SECRET: Optional[str] = None

    MAX_UPLOAD_MB: int = 20
    ALLOWED_MIME: str = "image/png,image/jpeg,application/pdf,text/plain"

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
