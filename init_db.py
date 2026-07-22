import asyncio
from sqlalchemy import text
from src.common.database import engine, Base
from src.api.models import Project, Artifact, DocumentChunks, Rules 

async def create_tables():
    print("Connecting to PostgreSQL engine...")
    async with engine.begin() as conn:
        print("Enabling pgvector extension...")
        # This registers the vector type natively in the database session loop
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
        print("Creating all schema tables...")
        await conn.run_sync(Base.metadata.create_all)
        
    print("Tables created successfully inside npi_db!")

if __name__ == "__main__":
    asyncio.run(create_tables())