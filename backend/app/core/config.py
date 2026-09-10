# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):

#     # -----------------------------------------
#     # APPLICATION
#     # -----------------------------------------

#     APP_NAME: str = "CraftMitra API"
#     APP_VERSION: str = "1.0.0"


#     # -----------------------------------------
#     # DATABASE
#     # -----------------------------------------

#     DATABASE_URL: str


#     # -----------------------------------------
#     # SECURITY
#     # -----------------------------------------

#     SECRET_KEY: str = "change-this-in-production"
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


#     # -----------------------------------------
#     # SUPABASE
#     # -----------------------------------------

#     SUPABASE_URL: str | None = None
#     SUPABASE_KEY: str | None = None
#     SUPABASE_BUCKET: str | None = None


#     # -----------------------------------------
#     # ENVIRONMENT
#     # -----------------------------------------

#     ENVIRONMENT: str = "development"


#     # -----------------------------------------
#     # SETTINGS CONFIGURATION
#     # -----------------------------------------

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore"
#     )


# settings = Settings()

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Always point at backend/.env, no matter which folder the app is
# launched from (root or backend/).
_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


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
    # CORS
    # -----------------------------------------

    # Comma-separated list of allowed frontend origins.
    # Local dev defaults cover Vite's default port; add the deployed
    # frontend URL here (via the .env file) before going live.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"


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
        env_file=_ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()