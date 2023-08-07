from fastapi import status, Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="x-api-key")

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    '''
    Get apikey from the header and check it
    '''
    if api_key_header == "BigProfiles-API":
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )