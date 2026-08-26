from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.logger import custom_logger as logger

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), 
    pool_pre_ping=True
)

logger.info("Motor PostgreSQL inicializado (Engine)")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)