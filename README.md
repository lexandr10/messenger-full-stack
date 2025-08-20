

# Messenger App
Це монорепозиторій з двох частин:

- **backend** (FastAPI + SQLAlchemy + WebSocket + PostgreSQL)  
- **frontend** (React.js + TailwindCSS)

---

# 📦 Backend

### 🚀 Швидкий старт

1. Скопіюйте приклад `.env` та заповніть змінні: 
``` bash 
cp .env

- POSTGRES_USER=
- POSTGRES_PASSWORD=
- POSTGRES_DB=
- POSTGRES_PORT=
- POSTGRES_HOST=

- DB_URL=

- CLD_NAME=
- CLD_API_KEY=
- CLD_API_SECRET=
- CLOUDINARY_URL=

- ACCESS_TOKEN_EXPIRE_MINUTES=30
- REFRESH_TOKEN_EXPIRE_DAYS=7
- ALGORITHM=HS256

- SECRET_KEY=secret

## Install dependencies:

- cd fastapi-backend
- poetry env use python3 
- poetry install --no-root

## Create Database in Docker

- docker compose up -d

## Active migration

- poetry run alembic upgrade head

## Turn on server 

- poetry run uvicorn src.main:app --reload --port (backend port)

# 📦 Frontend

## ENV file

- VITE_API_URL=http://localhost:8002/api (from your backend)
- VITE_WS_URL=ws://localhost:8002/ws (from your backend)

## Install dependencies:

- cd messenger-client
- yarn install

## Turn on server

- yarn dev

