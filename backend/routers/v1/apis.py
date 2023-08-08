from fastapi import APIRouter, Security, HTTPException, Response
from fastapi.responses import JSONResponse
from backend.components.schemas import EnrichInputModel, Entry, MessageOutputModel, ResultModel, EnrichModel
from backend.components.securitySchemas import get_api_key
from pydantic import ValidationError
import backend.main as main
from datetime import datetime
import random
import time
from collections import deque

import logging
logger = logging.getLogger("gunicorn.error")

iso_format = "%Y-%m-%d %H:%M:%S.%fZ"

router = APIRouter()

@router.post("/ingest", response_model = MessageOutputModel)
async def ingest(model: EnrichInputModel, x_api_key: str = Security(get_api_key)):
    '''
    Ingestion api

    Randomly create creation_datetime, response_time and response_code

    '''
    key = model.key
    payload = model.payload
    creation_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    response_time = random.randint(10, 50)
    response_code = random.choices([200, 500], weights=[90, 10], k=1)[0]

    try:
        entry = Entry(key=key, payload=payload, creation_datetime=creation_datetime, response_time=response_time, response_code=response_code)
        await main.app.state.mongo_database.save_entry(entry)
        output_message = MessageOutputModel(status_code=entry.response_code)
    except ValidationError as e:
        output_message = MessageOutputModel(status_code=422, message="Validation Error")

    return JSONResponse(content=output_message.dict(), status_code=output_message.status_code)


@router.get("/retrieve", response_model = ResultModel)
async def retrieve(date_from: str, date_to: str, x_api_key: str = Security(get_api_key)):
    '''
    Filter and create statistics from the database
    '''
    
    # Chek if date_from and date_to is ISO format
    try:
        datetime.fromisoformat(date_from[:-1])
        datetime.fromisoformat(date_to[:-1])
    except:
        error_msg = "Validation error"
        return JSONResponse(content={"detail": error_msg}, status_code=422)

    # Create pipeline for the stistics 
    pipeline = [
        {
            # Filter by date
            "$match": {
                "creation_datetime": {
                    "$gte": date_from,
                    "$lt": date_to
                }
            }
        },
        {
            # Trasform fiel in datetime for the croup task
            "$addFields": {
                "parsed_creation_datetime": {"$dateFromString": {"dateString": "$creation_datetime"}}
            }
        },
        {
            # aggregate 
            "$group": {
                "_id": {
                    "creation_datetime": {
                        "$dateToString": {
                            "format": "%Y-%m-%d %H:%M:000",
                            "date": "$parsed_creation_datetime"
                        }
                    },
                    "key": "$key"
                },
                "total_response_time_ms": {"$sum": "$response_time"}, # Sum response times
                "total_errors": {"$sum": {"$cond": [{"$eq": ["$response_code", 500]}, 1, 0]}}, # count all errors (with condition)
                "total_requests": {"$sum": 1} # Sum total aggregated requests
            }
        },
            {
                "$sort": {"_id.creation_datetime": -1}  # Sort by "minute" in descending order
            },
        {
            # output of the aggregation
            "$project": {
                "key": "$_id.key",
                "creation_datetime": "$_id.creation_datetime",
                "total_response_time_ms": 1,
                "total_errors": 1,
                "total_requests": 1,
                "_id": 0
            }
        }
    ]

    aggregation_result = await main.app.state.mongo_database.mongo_collections[main.app.state.mongo_database.collection].aggregate(pipeline, allowDiskUse=True).to_list(None)
    result_model = ResultModel()

    # Get aggregation data
    for entry in aggregation_result:
        result_model.values.append(EnrichModel(key=entry["key"] , creation_datetime=entry["creation_datetime"] , total_response_time_ms=entry["total_response_time_ms"] , total_requests=entry["total_requests"] , total_errors=entry["total_errors"]).dict())

    if len(aggregation_result) == 0:
        return result_model
    
    # Get the max last 10 items from the last aggregation period
    last_timestamp = aggregation_result[0]["creation_datetime"]+"Z"
    last_10_items = await main.app.state.mongo_database.mongo_collections[main.app.state.mongo_database.collection].find(
        {
            "creation_datetime": {"$gte": last_timestamp, "$lte": date_to},
        }
    ).sort("creation_datetime", -1).limit(10).to_list(None)

    for item in last_10_items:
        result_model.logs.append(Entry(key=item["key"], payload=item["payload"], creation_datetime=item["creation_datetime"], response_time=item["response_time"], response_code=item["response_code"]).dict())
    
    return JSONResponse(content=result_model.dict(), status_code=200)