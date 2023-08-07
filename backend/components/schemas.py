from pydantic import BaseModel, Field
from typing import List

class EnrichInputModel(BaseModel):
    '''
    Input model to de ingestion api
    '''
    key : int = Field(title="Key", description="Id della richiesta (deve essere un numero tra 1 e 6)")
    payload : str = Field(title="Payload", description="Payload della richiesta (una stringa da 10 a 255 caratteri)")

class EnrichModel(BaseModel):
    '''
    Model for output statistics
    '''
    key: int = Field(title="Key", description="Key of the record")
    creation_datetime: str = Field(title="Creation Datetime", description="Data di creazione del log aggregato")
    total_response_time_ms: int = Field(title="Total Response Time Ms", description="Tempo totale in millisecondi di tutte le risposte inviate nel log aggregato")
    total_requests: int = Field(title="Total Requests", description="Numero totale di tutte le risposte inviate nel log aggregato")
    total_errors: int = Field(title="Total Errors", description="Numero totale di tutte le risposte con un errore")

class Entry(BaseModel):
    '''
    Entry model to save on mongodb
    Key and payload ave validation checkers
    '''
    key : int = Field(ge=1, le=6, title="Key", description="Id della richiesta (deve essere un numero tra 1 e 6)")
    payload : str = Field(min_length=10, max_length=255, title="Payload", description="Payload della richiesta (una stringa da 10 a 255 caratteri)")
    creation_datetime: str = Field(title="Creation Datetime")
    response_time: int = Field(title="Response Time")
    response_code: int = Field(title="Response Code")

class ResultModel(BaseModel):
    '''
    Model to store statistic and the last 10 logs
    '''
    values: List[EnrichModel] = Field([], title="Values")
    logs: List[Entry] = Field([], title="Logs")

class MessageOutputModel(BaseModel):
    '''
    Message output model for the ingestion api
    '''
    status_code: int = Field(title="Status Code", description="Status code (numeric)")
    message: str = Field("Ingestion Complete", title="Message", description="Human readable message for understanding")

