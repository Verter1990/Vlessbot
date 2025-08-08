import asyncio
from core.database.database import async_session_maker
from core.database.models import Tariff
from sqlalchemy import select

async def check_tariffs():
    async with async_session_maker() as session:
        tariffs = (await session.execute(select(Tariff))).scalars().all()
        print(f'Tariffs found: {tariffs}')

if __name__ == "__main__":
    asyncio.run(check_tariffs())