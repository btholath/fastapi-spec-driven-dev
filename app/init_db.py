from app.models.annuity import Base
from sqlalchemy.ext.asyncio import create_async_engine
async def init_db():
    engine = create_async_engine("postgresql+asyncpg://postgres:admin@db:5432/postgres")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
import asyncio
asyncio.run(init_db())