from fastapi import WebSocket, status
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from src.conf.config import settings
from src.controllers.user_controller import UserController


async def authenticate_ws(ws: WebSocket, db: AsyncSession):
    auth = ws.headers.get("authorization") or ws.headers.get("Authorization")
    token = None
    if auth:
        parts = auth.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1].strip()

    if not token:
        token = ws.query_params.get("token")

    if not token:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token expired")
        return None
    except jwt.PyJWTError:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return None

    username = payload.get("sub")
    if not username:
        await ws.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token payload"
        )
        return None

    user = await UserController(db).get_user_by_username(username)
    if not user:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
        return None

    ws.state.user = user
    ws.state.jwt_payload = payload

    return user
