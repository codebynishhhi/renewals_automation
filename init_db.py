import asyncio
from sqlalchemy import text
from src.common.database import Base, engine
from src.api.models import Project, Artifact, DocumentChunks, Rules

async def init_db():
    print("Connecting to database...")
    async with engine.begin() as connection:
        # 1. Enable the vector extension explicitly inside npi_db
        print("Enabling pgvector extension...")
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
        # 2. Re-run the table generator task
        print("Generating database tables...")
        await connection.run_sync(Base.metadata.create_all)
        
    print("\n🎉 ALL TABLES CREATED PERFECTLY INSIDE NPI_DB! 🎉\n")

if __name__ == "__main__":
    asyncio.run(init_db())
