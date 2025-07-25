import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import random

from core.database.models import User, Server, Tariff, Subscription, Transaction, GiftCode
from core.database.database import async_session_maker, init_db, async_engine, Base



@pytest.mark.asyncio
class TestUserCRUD:
    async def test_create_user(self, session: AsyncSession):
        unique_id = random.randint(100000, 999999) # Generate a unique ID
        user = User(telegram_id=unique_id, username=f"testuser_{unique_id}", language_code="en")
        session.add(user)
        # No commit here, rely on the session's transaction
        await session.flush() # Flush to get the ID if needed, but not strictly necessary for this test

        fetched_user = await session.get(User, user.id)
        assert fetched_user is not None
        assert fetched_user.telegram_id == unique_id
        assert fetched_user.username == f"testuser_{unique_id}"

    async def test_read_user(self, session: AsyncSession):
        unique_id = random.randint(100000, 999999)
        user = User(telegram_id=unique_id, username=f"readuser_{unique_id}", language_code="ru")
        session.add(user)
        await session.flush() # Flush to make it available for query

        fetched_user = await session.execute(select(User).where(User.telegram_id == unique_id))
        fetched_user = fetched_user.scalars().first()
        assert fetched_user is not None
        assert fetched_user.username == f"readuser_{unique_id}"

    async def test_update_user(self, session: AsyncSession):
        unique_id = random.randint(100000, 999999)
        user = User(telegram_id=unique_id, username=f"oldname_{unique_id}", language_code="en")
        session.add(user)
        await session.flush()

        user.username = f"newname_{unique_id}"
        user.unassigned_days = 10
        await session.flush() # Flush changes to the database

        fetched_user = await session.get(User, user.id)
        assert fetched_user.username == f"newname_{unique_id}"
        assert fetched_user.unassigned_days == 10

    async def test_delete_user(self, session: AsyncSession):
        unique_id = random.randint(100000, 999999)
        user = User(telegram_id=unique_id, username=f"deleteuser_{unique_id}", language_code="en")
        session.add(user)
        await session.flush()

        await session.delete(user)
        await session.flush()

        fetched_user = await session.get(User, user.id)
        assert fetched_user is None

@pytest.mark.asyncio
class TestServerCRUD:
    async def test_create_server(self, session: AsyncSession):
        unique_id = random.randint(1000, 9999)
        server = Server(name=f"TestServer1_{unique_id}", api_url=f"http://api1.com/{unique_id}", api_user=f"user1_{unique_id}", api_password=f"pass1_{unique_id}", inbound_id=unique_id)
        session.add(server)
        await session.flush()

        fetched_server = await session.get(Server, server.id)
        assert fetched_server is not None
        assert fetched_server.name == f"TestServer1_{unique_id}"

    async def test_read_server(self, session: AsyncSession):
        unique_id = random.randint(1000, 9999)
        server = Server(name=f"TestServer2_{unique_id}", api_url=f"http://api2.com/{unique_id}", api_user=f"user2_{unique_id}", api_password=f"pass2_{unique_id}", inbound_id=unique_id)
        session.add(server)
        await session.flush()

        fetched_server = await session.execute(select(Server).where(Server.name == f"TestServer2_{unique_id}"))
        fetched_server = fetched_server.scalars().first()
        assert fetched_server is not None
        assert fetched_server.api_url == f"http://api2.com/{unique_id}"

    async def test_update_server(self, session: AsyncSession):
        unique_id = random.randint(1000, 9999)
        server = Server(name=f"TestServer3_{unique_id}", api_url=f"http://api3.com/{unique_id}", api_user=f"user3_{unique_id}", api_password=f"pass3_{unique_id}", inbound_id=unique_id)
        session.add(server)
        await session.flush()

        server.api_url = f"http://newapi3.com/{unique_id}"
        server.is_active = False
        await session.flush()

        fetched_server = await session.get(Server, server.id)
        assert fetched_server.api_url == f"http://newapi3.com/{unique_id}"
        assert fetched_server.is_active is False

    async def test_delete_server(self, session: AsyncSession):
        unique_id = random.randint(1000, 9999)
        server = Server(name=f"TestServer4_{unique_id}", api_url=f"http://api4.com/{unique_id}", api_user=f"user4_{unique_id}", api_password=f"pass4_{unique_id}", inbound_id=unique_id)
        session.add(server)
        await session.flush()

        await session.delete(server)
        await session.flush()

        fetched_server = await session.get(Server, server.id)
        assert fetched_server is None

@pytest.mark.asyncio
class TestTariffCRUD:
    async def test_create_tariff(self, session: AsyncSession):
        unique_id = random.randint(100, 999)
        tariff = Tariff(name={"ru": f"Тест_{unique_id}", "en": f"Test_{unique_id}"}, duration_days=30, price_rub=10000, price_stars=100)
        session.add(tariff)
        await session.flush()

        fetched_tariff = await session.get(Tariff, tariff.id)
        assert fetched_tariff is not None
        assert fetched_tariff.name["ru"] == f"Тест_{unique_id}"

    async def test_read_tariff(self, session: AsyncSession):
        unique_id = random.randint(100, 999)
        tariff = Tariff(name={"ru": f"Чтение_{unique_id}", "en": f"Read_{unique_id}"}, duration_days=60, price_rub=20000, price_stars=200)
        session.add(tariff)
        await session.flush()

        fetched_tariff = await session.execute(select(Tariff).where(Tariff.duration_days == 60))
        fetched_tariff = fetched_tariff.scalars().first()
        assert fetched_tariff is not None
        assert fetched_tariff.price_rub == 20000

    async def test_update_tariff(self, session: AsyncSession):
        unique_id = random.randint(100, 999)
        tariff = Tariff(name={"ru": f"Обновление_{unique_id}", "en": f"Update_{unique_id}"}, duration_days=90, price_rub=30000, price_stars=300)
        session.add(tariff)
        await session.flush()

        tariff.price_rub = 35000
        tariff.is_active = False
        await session.flush()

        fetched_tariff = await session.get(Tariff, tariff.id)
        assert fetched_tariff.price_rub == 35000
        assert fetched_tariff.is_active is False

    async def test_delete_tariff(self, session: AsyncSession):
        unique_id = random.randint(100, 999)
        tariff = Tariff(name={"ru": f"Удаление_{unique_id}", "en": f"Delete_{unique_id}"}, duration_days=10, price_rub=5000, price_stars=50)
        session.add(tariff)
        await session.flush()

        await session.delete(tariff)
        await session.flush()

        fetched_tariff = await session.get(Tariff, tariff.id)
        assert fetched_tariff is None
