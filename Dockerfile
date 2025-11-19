FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# Force IPv4 (fix Supabase connections on Render)
RUN echo 'precedence ::ffff:0:0/96  100' >> /etc/gai.conf

WORKDIR /chatbot

COPY requirements.txt /chatbot/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /chatbot/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
