from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# DATABASE_URL = "postgresql://user:h4ssl3.Fr33@db:5432/hasslefreecomputers"
DATABASE_URL = "postgresql+psycopg2://user00:chocolatecake@localhost:5433/user00"
engine = create_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool
)
database_engine = engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()