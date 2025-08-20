from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import (
    auth_routes,
    conversation_routers,
    upload_routers,
    message_routers,
)
from src.sockets import routes


app = FastAPI(title="Messenger API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You use your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/api")
app.include_router(conversation_routers.router, prefix="/api")
app.include_router(upload_routers.router, prefix="/api")
app.include_router(message_routers.router, prefix="/api")
app.include_router(routes.ws_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
