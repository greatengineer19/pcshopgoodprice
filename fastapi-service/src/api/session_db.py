from src.database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import AsyncGenerator, Annotated
from fastapi import Depends

AsyncSessionLocal = async_sessionmaker(...)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

AsyncDbSession = Annotated[AsyncSession, Depends(get_db_async)]