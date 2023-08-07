# Introduction
REST API projet that uses FastAPI, MongoDB, Motor (the async Python driver for MongoDB) and docker-compose.<br />

# Quickstart

First, clone this repository:

    git clone git@github.com:silviuspac/test_tecnico_BigProfiles.git

Then, go to the project folder and start the service:

    cd test_tecnico_BigProfiles
    ./bin/start.sh

This bash script calls docker-compose that buids the dockers (with the libraries from the requirements.txt) and starts them. <br />
Now the application is running on the localhost and listening on port 8000.

If the user wants to change global variables, the .env file can be modified.

To stop the application:

    ./bin/stop.sh

# APIs
The project implements two APIs:

| HTTP Verbs | Endpoints | Action |
| --- | --- | --- |
| POST | /api/v1/ingest | To add a new entry in the  |
| GET | /api/v1/retrieve | To retrieve all causes on the platform |

    - ingest: take in input a int key and a string payload, this api has a randomized behaviour. 
    - retrieve: that filters the database based on date-time and returns some statistics

## Ingestion 
Takes in input two values: <br />

    - key: an integer between 1 and 6
    - payload: a string of variable length from 10 to 255

The api takes this two input values and with randomized behaviour creates other fields and saves them on the MongoDB database.<br />
All the fields saved are:

    - key: key of the request
    - payload: payload of the request
    - creation_datetime: datetime in which the request arrived
    - response_time: random integer between 10 and 50, indicates the response time
    - response_code: response code 200 or 500 (with 10% probability) 

## Retrieve
Takes in input two values: <br />

    - date_from: starting datetime in ISO format
    - date-to: ending datetime in ISO format

This api aggregates pet minute the data between date_from and date_to, giving in output some statistics and the last 10 logs from the last aggregation period.

## API Security (Api Key)
For the security of the APIs calls the header of both APIs has the parameter "x-api-key".

# Technologies Used
* [MongoDB](https://www.mongodb.com/) This is a free open source NOSQL document database with scalability and flexibility. Data are stored in flexible JSON-like documents.
  
* [FastAPI](https://fastapi.tiangolo.com/) This is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.

* [Motor](https://www.mongodb.com/docs/drivers/motor/) This presents a coroutine-based API for non-blocking access to MongoDB from Tornado or asyncio.

* [Docker](https://www.docker.com/) This is a software platform that allows you to build, test, and deploy applications quickly.

* [Docker Compose](https://docs.docker.com/compose/) This is a tool for defining and running multi-container Docker applications.

* [Dozzle](https://dozzle.dev/) This is a lightweight, web-based Docker log viewer that provides real-time monitoring and easy troubleshooting.

* [Mongo Express](https://github.com/mongo-express/mongo-express) This is a web-based MongoDB admin interface

# Tests
In the test folder, some unit tests are proposed to assess the behaviour of the APIs, to run them:

    python tests/tests.py

In the same folder, also two other files can be found. In those, API calls in multithreading enviroment are called in order to test the performance of the application. 