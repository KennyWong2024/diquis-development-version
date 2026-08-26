from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from pydantic_core import MultiHostUrl
from typing import List, Optional

class Settings(BaseSettings):
    # ── Proyecto ──
    PROJECT_NAME: str = "Diquis Local"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    # ── JWT y Seguridad ──
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── PostgreSQL Local ──
    POSTGRES_HOST: Optional[str] = "127.0.0.1"
    POSTGRES_USER: Optional[str] = "postgres"
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = "diquis"
    POSTGRES_PORT: Optional[int] = 5432
    DATABASE_URL: Optional[str] = None
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # ── Email (Opcional — en modo local se loggea en consola) ──
    RESEND_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@diquis.local"
    FRONTEND_URL: str = "http://localhost:5173"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_HOST, self.POSTGRES_DB]):
            raise ValueError("Faltan credenciales de BD. Define DATABASE_URL o las variables POSTGRES_*")

        return str(MultiHostUrl.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        ))

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()