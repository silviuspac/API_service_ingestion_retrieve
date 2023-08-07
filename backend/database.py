from motor.motor_asyncio import AsyncIOMotorClient
import motor
import ujson
import backend.main as main
from queue import Queue
from backend.components.schemas import Entry
from typing import List
import time
import asyncio
from contextlib import suppress
from pymongo import MongoClient, InsertOne
from fastapi.encoders import jsonable_encoder

import logging
logger = logging.getLogger("gunicorn.error")

class MongoDatabase():
    '''
    Class to manage mongodb operations 
    '''
    
    def __init__(self, db_url: str, db_name: str, collection: str):
        # Create mongo client and colletions
        self.mongo_client = AsyncIOMotorClient(db_url)
        self.mongo_client._json_lib = ujson # Faster than json
        self.mongo_database = self.mongo_client[db_name]
        self.mongo_collections = { collection: self.mongo_database.get_collection(collection), }

        self.collection = collection

        # Create a single-field index on the "creation_datetime" field
        # To speedup queries
        self.mongo_collections[collection].create_index("creation_datetime", background=True)

        # Define async queue used for bulk_write
        self.entry_queue = asyncio.Queue(1000)
        self.buffer_size = 100
        
    async def get_queue_items(self, count: int):
        '''
        Get list of Items from the queue
        '''
        items = []
        while not self.entry_queue.empty() and len(items) < count:
            items.append(await self.entry_queue.get())
        return items
    
    async def perform_bulk_insert(self, entries):
        '''
        Create operations and insert in bulk
        '''
        
        bulk_operations = [InsertOne(entry) for entry in entries]
        await self.mongo_collections[self.collection].bulk_write(bulk_operations, ordered=False)
        


    async def save_entry(self, entry: Entry):
        '''
        Add entries
        '''
        # put entries in queue
        await self.entry_queue.put(entry)

        if self.entry_queue.qsize() >= self.buffer_size:
            # List comprehension to get ditc from entries 
            entries_to_save = [entries.dict() for entries in list(await self.get_queue_items(self.buffer_size))]
            try:
                await self.perform_bulk_insert(entries_to_save)
            except Exception as e:
                print(f"Error occurred during bulk insert: {e}")
    
    async def save_remaining_entries(self):
        '''
        Function to seve remaining entries
        '''
        entries_to_save = [entries.dict() for entries in list(await self.get_queue_items(self.buffer_size))]
        if entries_to_save:
            await self.perform_bulk_insert(entries_to_save)

    async def save_remaining_entries_periodically(self):
        '''
        Function to trigger save_remaining_entries_periodically()
        '''
        while True:
            await asyncio.sleep(10)  # Save remaining entries every 10 seconds
            await self.save_remaining_entries()


async def init_mongodb(db_name: str, db_url: str, collection: str):
    """
    Init a mongo db database
    Args:
        db_name: name of the database
        db_url: url of the database
        collection: name of a collection

    Returns:
        mongo_database: MongoDatabase
    """
    mongo_database = MongoDatabase(db_url, db_name, collection)

    return mongo_database


async def get_mongo_meta() -> dict:
    '''
    Function used in health check api
    '''

    list_databases = await main.app.state.mongo_database.mongo_client.list_database_names()
    list_of_collections = {}
    for db in list_databases:
        logger.info(db)
        list_of_collections[db] = await main.app.state.mongo_database.mongo_client[db].list_collection_names()
    mongo_meta = await main.app.state.mongo_database.mongo_client.server_info()
    return {"version": mongo_meta["version"], "databases": list_databases, "collections": list_of_collections}