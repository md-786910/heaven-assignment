from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/issue_tracker"

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Issue Tracker API"

    # JWT/Security Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days

    class Config:
        env_file = ".env"


settings = Settings()
