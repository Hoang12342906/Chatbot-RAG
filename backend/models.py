from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from database import Base
import datetime

class ChatMessage(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100))
    sender = Column(Enum('user', 'bot'))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
