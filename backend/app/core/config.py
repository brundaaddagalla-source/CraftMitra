from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # -----------------------------------------
    # APPLICATION
    # -----------------------------------------

    APP_NAME: str = "CraftMitra API"
    APP_VERSION: str = "1.0.0"


    # -----------------------------------------
    # DATABASE
    # -----------------------------------------

    DATABASE_URL: str


    # -----------------------------------------
    # SECURITY
    # -----------------------------------------

    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    # -----------------------------------------
    # SUPABASE
    # -----------------------------------------

    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None
    SUPABASE_BUCKET: str | None = None


    # -----------------------------------------
    # ENVIRONMENT
    # -----------------------------------------

    ENVIRONMENT: str = "development"


    # -----------------------------------------
    # SETTINGS CONFIGURATION
    # -----------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()