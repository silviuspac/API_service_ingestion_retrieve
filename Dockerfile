FROM python:3.8.10
WORKDIR ./backend
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt