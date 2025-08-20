from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[int, Set[WebSocket]] = {}

    async def connect(self, room_id: int, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room_id, set()).add(ws)

    async def disconnect(self, room_id: int, ws: WebSocket):
        peers = self.rooms.get(room_id)
        if not peers:
            return

        peers.discard(ws)
        if not peers:
            self.rooms.pop(room_id, None)

    async def broadcast(self, room_id: int, data: dict):
        for ws in list(self.rooms.get(room_id, ())):
            try:
                await ws.send_json(data)
            except Exception:
                await self.disconnect(room_id, ws)
