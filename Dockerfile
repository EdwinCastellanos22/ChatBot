FROM python:3.12-slim

WORKDIR /chatbot

COPY requirements.txt /chatbot/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /chatbot/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
