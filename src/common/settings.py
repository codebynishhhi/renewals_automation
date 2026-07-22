import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # llm 
    model_name : str = os.getenv("MODEL_NAME")
    groq_api_key:str = os.getenv("GROQ_API_KEY")

    # langfuse observability 
    langfuse_public_key :str  = ""
    langfuse_secret_key:str = ""
    langfuse_host:str = "https://cloud.langfuse.com"

    # database 
    db_host :str = "localhost"
    db_port : int = 5432
    db_name : str = "npi_db"
    db_username :str = "npi_user"
    db_password :str = "npi_password"

    # minio
    minio_endpoint : str = "localhost:9000"
    minio_access_key : str = "minioadmin"
    minio_secret_key : str = "minioadmin"
    minio_bucket : str = "npi_artifacts"
    minio_secure : bool = False

    # app
    log_level:str = "INFO"
    app_env:str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # ignore unknown vars in .env by using extra = "ignore"
        extra="ignore"
    )

    # Database connection and alembic 
    @property
    def database_url(self) -> str:
        """ Async used by sqlalchemy engine"""
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    @property
    def database_url_sync(self) -> str:
        """ SYNC used by alembic only """
        # Appended +asyncpg here
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Settings() tells Python to execute the constructor method.
    # This prompts Pydantic to read your .env file, populate all your settings fields, and return a valid object instance containing your variables.
    return Settings()

settings = get_settings()