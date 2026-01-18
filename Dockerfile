FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /chatbot

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /chatbot/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /chatbot/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
