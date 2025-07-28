from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from config import setting
import os

web_environment = os.environ.get('WEB_ENVIRONMENT')
if web_environment == 'staging':
    DATABASE_URL = f"{setting.DB_STAGING_ENGINE}://{setting.DB_STAGING_USERNAME}{setting.DB_STAGING_PASSWORD}@{setting.DB_STAGING_HOST}:{setting.DB_STAGING_PORT}/{setting.DB_STAGING_DATABASE}"
elif web_environment == 'production':
    DATABASE_URL = f"{setting.DB_PRODUCTION_ENGINE}://{setting.DB_PRODUCTION_USERNAME}{setting.DB_PRODUCTION_PASSWORD}@{setting.DB_PRODUCTION_HOST}:{setting.DB_PRODUCTION_PORT}/{setting.DB_PRODUCTION_DATABASE}"
else:
    DATABASE_URL = f"{setting.DB_TEST_ENGINE}://{setting.DB_TEST_USERNAME}{setting.DB_TEST_PASSWORD}@{setting.DB_TEST_HOST}:{setting.DB_TEST_PORT}/{setting.DB_TEST_DATABASE}"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool
)

database_engine = engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()