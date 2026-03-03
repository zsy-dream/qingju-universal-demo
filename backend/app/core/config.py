from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Qingju-Universal"
    API_V1_STR: str = "/api/v1"

    SQLITE_DB_PATH: str = "./data/app.db"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    MOCK_MODE: bool = True


settings = Settings()
