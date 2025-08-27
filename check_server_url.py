import asyncio
from sqlalchemy import select
from core.database.database import async_session_maker
from core.database.models import Server

async def main():
    print("Querying servers from the database...")
    async with async_session_maker() as session:
        stmt = select(Server)
        result = await session.execute(stmt)
        servers = result.scalars().all()

        if not servers:
            print("No servers found in the database.")
        else:
            print(f"Found {len(servers)} server(s):")
            for server in servers:
                print(f"  - ID: {server.id}")
                print(f"    Name: {server.name}")
                print(f"    API URL: {server.api_url}")
                print("----")

if __name__ == "__main__":
    asyncio.run(main())
