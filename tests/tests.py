import requests

ingest_url = "http://localhost:8000/api/v1/ingest"
retrieve_url = "http://localhost:8000/api/v1/retrieve"

def test_ingest_api():
    '''
    Test if the response code and message are correct
    '''
    headers={"x-api-key" : 'BigProfiles-API'}
    data = {
        "key": 2,
        "payload": "stringstringstring"
    }

    # Make the POST request
    response = requests.post(ingest_url, json=data, headers=headers)
    json_response = response.json()

    # Check the response
    assert response.status_code == 200 or response.status_code == 500
    assert json_response["message"] == "Ingestion Complete"
    assert json_response["status_code"] == response.status_code

def test_ingest_api_validation_error_key():
    '''
    Test validation error on key
    '''
    headers={"x-api-key" : 'BigProfiles-API'}
    data = {
        "key": 0,
        "payload": "stringstringstring"
    }

    # Make the POST request
    response = requests.post(ingest_url, json=data, headers=headers)
    json_response = response.json()

    # Check the response
    assert response.status_code == 422
    assert json_response["message"] == "Validation Error"
    assert json_response["status_code"] == response.status_code

def test_ingest_api_validation_error_payload():
    '''
    Test validation error on payload
    '''
    headers={"x-api-key" : 'BigProfiles-API'}
    data = {
        "key": 2,
        "payload": "string"
    }

    # Make the POST request
    response = requests.post(ingest_url, json=data, headers=headers)
    json_response = response.json()

    # Check the response
    assert response.status_code == 422
    assert json_response["message"] == "Validation Error"
    assert json_response["status_code"] == response.status_code

def test_retrieve_api_validation_error():
    '''
    Test validation error on date
    '''
    data = {
        "date_from": "aaaa",
        "date_to": "2023-08-09 13:50:00.000Z"
    }
    headers={"x-api-key" : 'BigProfiles-API'}
    response = requests.get(retrieve_url, params=data, headers=headers)
    assert response.status_code == 422

def test_retrieve_api():
    '''
    Test if status code is right
    '''
    data = {
        "date_from": "2023-08-06 13:50:00.000Z",
        "date_to": "2023-08-09 13:50:00.000Z"
    }
    headers={"x-api-key" : 'BigProfiles-API'}
    response = requests.get(retrieve_url, params=data, headers=headers)

    assert response.status_code == 200

def test_wrong_api_key():
    '''
    Test if status code is right
    '''
    data = {
        "date_from": "2023-08-06 13:50:00.000Z",
        "date_to": "2023-08-09 13:50:00.000Z"
    }
    headers={"x-api-key" : 'test'}
    response = requests.get(retrieve_url, params=data, headers=headers)
    json_response = response.json()

    assert response.status_code == 401
    assert json_response["detail"] == "Invalid or missing API Key"

if __name__ == '__main__':
    test_ingest_api()
    test_ingest_api_validation_error_key()
    test_ingest_api_validation_error_payload()
    test_retrieve_api()
    test_wrong_api_key()

    print("Passed all tests!")