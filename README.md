# 🚀 ChatBot Django
ChatBot Django es una plataforma moderna para **chat en tiempo real**, construida sobre un backend robusto usando **WebSockets**, **Redis** y **Django Channels**, combinada con una API segura con **Django REST Framework** y **JWT** para autenticación.  
Este proyecto provee:

- 💬 Chat en tiempo real (WebSockets)
- 🔐 Autenticación JWT (login, refresh, protección de rutas)
- ⚡ Mensajería persistente usando PostgreSQL
- 🧵 Canales en vivo con Django Channels
- 🚀 Cola de mensajes y presencia usando Redis
- 🗄️ Supabase como herramienta integral (almacenamiento, administración, observabilidad)
- 🐳 Entorno Dockerizado
- 🛡 Arquitectura limpia y escalable

---

## 📦 Tecnologías principales
| Tecnología | Uso |
|-----------|-----|
| Django | Core backend / ORM |
| Django REST Framework | API REST |
| Channels | WebSockets |
| Redis | Broker para WebSockets / presencia |
| PostgreSQL | Base de datos |
| Supabase | Hosting / administración / monitoreo |
| JWT (SimpleJWT) | Autenticación |
| Docker & Docker Compose | Entorno reproducible |

---

# 📁 Estructura del proyecto
| Carpeta/Archivo     | Descripción |
|---------------------|-------------|
| `api/`              | API REST con DRF (JWT, auth, endpoints) |
| `chat/`             | Consumers WebSocket, routing, views |
| `ChatBot/`          | Settings, ASGI, WSGI, URLs |
| `middleware/`       | Middlewares personalizados |
| `utils/`            | Cliente Supabase e integraciones |
| `static/`           | Archivos estáticos (JS, CSS) |
| `templates/`        | Templates HTML (login, chat) |
| `logs/`             | Logs del sistema, API y errores |
| `docker-compose.yml`| Orquestación de servicios |
| `Dockerfile`        | Imagen Docker del backend |
| `requirements.txt`  | Dependencias del proyecto |
| `manage.py`         | CLI de Django |



---

# ⚙️ Configuración del entorno

## 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/EdwinCastellanos22/ChatBot.git
cd ChatBot
```

## 2️⃣ Configurar variables de entorno
DEBUG=True
SECRET_KEY=tu_secret_key

POSTGRES_DB=chatbot
POSTGRES_USER=chatuser
POSTGRES_PASSWORD=chatpass
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

# JWT
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440

## 3️⃣ Crear entorno virtual y instalar dependencias
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4️⃣ Iniciar el servidor
```bash
python manage.py runserver
```

## 5️⃣ Acceder al chat
Abre tu navegador y ve a http://localhost:8000

## 6️⃣ Dockerizar el proyecto
```bash
docker-compose up --build
```
