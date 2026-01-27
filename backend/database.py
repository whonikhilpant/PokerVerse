from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use environment variable or default local postgres
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:password@localhost/pokerverse")

engine = create_async_engine(DATABASE_URL, echo=True)

# Factory for creating new database sessions
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()

# Dependency to get DB session in endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
