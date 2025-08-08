#!/bin/bash
docker-compose exec app python -c '''
from core.database.database import async_session_maker
from core.database.models import Tariff
from sqlalchemy import select
import asyncio

async def get_tariffs():
    async with async_session_maker() as session:
        result = await session.execute(select(Tariff))
        tariffs = result.scalars().all()
        print('Current Tariffs:')
        if tariffs:
            for t in tariffs:
                # Assuming Tariff.name is a JSON field and you want the 'ru' key
                # If Tariff.name is a simple string, use t.name directly
                name_display = t.name.get('ru', str(t.name)) if isinstance(t.name, dict) else str(t.name)
                print(f'- ID: {t.id}, Name: {name_display}, Duration: {t.duration_days} days, Price: {t.price_rub} RUB')
        else:
            print('No tariffs found.')
        await session.close()
        # async_session_maker.bind.dispose() # This might close the engine for future calls in the same process, remove if you plan more operations

asyncio.run(get_tariffs())
'''