from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String, index=True)
    sender = Column(String)          # "user" or "ai"
    content = Column(Text)
    sentiment = Column(String, default="neutral")
    timestamp = Column(DateTime, default=datetime.utcnow)