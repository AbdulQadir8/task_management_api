import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings - using the provided Neon connection string
    postgres_user: str = os.getenv("POSTGRES_USER", "neondb_owner")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "npg_HGgtQjuWSI73")
    postgres_host: str = os.getenv("POSTGRES_HOST", "ep-royal-cherry-ahlsuukg-pooler.c-3.us-east-1.aws.neon.tech")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_db: str = os.getenv("POSTGRES_DB", "neondb")
    neon_branch: str = os.getenv("NEON_BRANCH", "main")

    # Construct the database URL
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}?sslmode=require&channel_binding=require"

    # For local development with SQLite fallback
    use_sqlite_fallback: bool = os.getenv("USE_SQLITE_FALLBACK", "false").lower() == "true"

    @property
    def fallback_database_url(self) -> str:
        return "sqlite:///./task_management_local.db"

settings = Settings()