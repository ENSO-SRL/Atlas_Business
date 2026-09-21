from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    CLIENT_API_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file="src/.env")
