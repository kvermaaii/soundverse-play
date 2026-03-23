from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql://soundverse:soundverse@localhost:5432/soundverse"
    APP_NAME: str = "Soundverse Play API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_KEY: str = "default-dev-key"
    STREAM_CHUNK_SIZE: int = 8192


settings = Settings()
