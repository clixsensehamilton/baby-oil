"""
Application configuration loaded from environment variables.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration — reads from .env or environment."""

    # --- Database (Neon DB) ---
    DATABASE_URL: str = Field(
        default="postgresql://user:pass@localhost:5432/oil_intel",
        description="Neon DB connection string",
    )

    # --- OpenAI ---
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="Model for scoring")

    # --- CORS ---
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed frontend origins",
    )

    # --- Scraper Schedule ---
    SCRAPE_INTERVAL_MINUTES: int = Field(
        default=15, description="Minutes between scrape cycles"
    )

    # --- NASA FIRMS ---
    NASA_FIRMS_MAP_KEY: str = Field(
        default="", description="NASA FIRMS MAP_KEY for satellite thermal data"
    )

    # --- ACLED (Conflict Data) ---
    ACLED_API_KEY: str = Field(default="", description="ACLED API key")
    ACLED_EMAIL: str = Field(default="", description="Email registered with ACLED")

    # --- EIA (US Gov Petroleum Data) ---
    EIA_API_KEY: str = Field(default="", description="EIA API key")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
