FROM python:3.11.4
WORKDIR /backend
COPY requirements.txt .
RUN pip install -r requirements.txt