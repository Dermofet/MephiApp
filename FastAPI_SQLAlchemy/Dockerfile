FROM python:3.10.7
WORKDIR /FastAPI_SQLAlchemy

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements .
RUN pip install -r requirements

COPY . .