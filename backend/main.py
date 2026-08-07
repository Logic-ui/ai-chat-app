from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, List
import json

from database import engine, get_db, Base
from models import Message
from ai_service import analyze_sentiment, generate_ai_reply

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-Time AI Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_id: str, ws: WebSocket):
        await ws.accept()
        self.active_connections.setdefault(room_id, []).append(ws)

    def disconnect(self, room_id: str, ws: WebSocket):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(ws)

    async def broadcast(self, room_id: str, message: dict):
        for connection in self.active_connections.get(room_id, []):
            await connection.send_json(message)

manager = ConnectionManager()


@app.get("/history/{room_id}")
def get_history(room_id: str, db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(Message.room_id == room_id).order_by(Message.timestamp).all()
    return [
        {"sender": m.sender, "content": m.content, "sentiment": m.sentiment, "timestamp": m.timestamp}
        for m in msgs
    ]


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    db = next(get_db())

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            user_text = data.get("content", "")

            # Save + broadcast user message immediately (real-time feel)
            sentiment = await analyze_sentiment(user_text)
            user_msg = Message(room_id=room_id, sender="user", content=user_text, sentiment=sentiment)
            db.add(user_msg)
            db.commit()

            await manager.broadcast(room_id, {
                "sender": "user", "content": user_text, "sentiment": sentiment
            })

            # Notify typing, then generate AI reply
            await manager.broadcast(room_id, {"sender": "ai", "typing": True})

            history = db.query(Message).filter(Message.room_id == room_id).order_by(
                Message.timestamp.desc()
            ).limit(6).all()
            history_payload = [
                {"role": "user" if m.sender == "user" else "assistant", "content": m.content}
                for m in reversed(history)
            ]

            ai_reply = await generate_ai_reply(history_payload, user_text)
            ai_msg = Message(room_id=room_id, sender="ai", content=ai_reply)
            db.add(ai_msg)
            db.commit()

            await manager.broadcast(room_id, {
                "sender": "ai", "content": ai_reply, "typing": False
            })

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)