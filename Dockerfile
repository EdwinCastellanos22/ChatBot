# Crear imagen base para el contenedor
FROM python:3.12-slim

# Evitar buffering del output
ENV PYTHONUNBUFFERED=1

# Crear carpeta de trabajo
WORKDIR /chatbot

# Copiar los requerimentos e instalar librerias
COPY requirements.txt /chatbot/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . /chatbot/

# Exponer puerto 8000
EXPOSE 8000

# Ejecutar contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
