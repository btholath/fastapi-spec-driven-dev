from app.models.annuity import Base
from sqlalchemy.ext.asyncio import create_async_engine
async def init_db():
    engine = create_async_engine("postgresql+asyncpg://postgres:admin@192.168.144.1:5433/postgres")
    async with engine.begin() as conn:
        # Drop existing tables to avoid conflicts
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
import asyncio
asyncio.run(init_db())