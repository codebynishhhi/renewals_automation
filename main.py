from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes import project, artifacts
from src.common.logging_config import setup_logging
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app : FastAPI):
    """  Runs once at startup """
    setup_logging()
    yield

app = FastAPI(title="Renewals Automation", version="0.1.0", lifespan=lifespan)

# router to modules
app.include_router(project.router)
app.include_router(artifacts.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all websites/browsers (like Swagger UI) to connect
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, PUT, DELETE)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/health")
async def health():
    return {"status":"ok"}