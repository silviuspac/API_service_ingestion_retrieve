from fastapi import FastAPI
from backend.database import init_mongodb, get_mongo_meta
from backend.routers.v1.apis import router as v1
import asyncio
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

MONGO_DB = os.getenv('MONGO_DB')
MONGO_URL = os.getenv('MONGO_URL')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')

import logging

app = FastAPI()

app.include_router(v1, prefix="/api/v1")

logger = logging.getLogger("gunicorn.error")

@app.on_event("startup")
async def startup_event():
    '''
    - Inizialize the database at the startup
    - Create async task that periodicaly save remaining entries in queue
    '''
    print(MONGO_DB, MONGO_URL, MONGO_COLLECTION)
    app.state.mongo_database = await init_mongodb(
        MONGO_DB, MONGO_URL, MONGO_COLLECTION
    )
    asyncio.create_task(app.state.mongo_database.save_remaining_entries_periodically())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Closing app")


@app.get("/health-check")
async def health_check():
    logger.info("Health check")

    return await get_mongo_meta()