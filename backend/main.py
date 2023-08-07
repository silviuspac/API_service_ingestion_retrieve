from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from backend.database import init_mongodb, get_mongo_meta
from backend.routers.v1.apis import router as v1
import asyncio

import logging

app = FastAPI()

app.include_router(v1, prefix="/api/v1")

logger = logging.getLogger("gunicorn.error")
logger.info("Si parte")

@app.on_event("startup")
async def startup_event():
    '''
    - Inizialize the database at the startup
    - Create async task that periodicaly save remaining entries in queue
    '''
    logger.info("Starting the database")
    app.state.mongo_database = await init_mongodb(
        "testdb", "mongodb://root:password@mongo:27017/?retryWrites=true&w=majority", "apis"
    )
    asyncio.create_task(app.state.mongo_database.save_remaining_entries_periodically())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Closing app")


@app.get("/health-check")
async def health_check():
    logger.info("Health check")

    return await get_mongo_meta()