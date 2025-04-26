from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import ask_question
import shutil
import os
from chatbot import create_vectorstore_from_pdf
from typing import List
from fastapi import Depends
from database import Base
from database import SessionLocal  
from models import ChatMessage
from sqlalchemy.orm import Session
from sqlalchemy import distinct

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

#allow access from frontend react
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change back later if security is needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Định nghĩa request model để nhận dữ liệu JSON
class Message(BaseModel):
    type: str
    text: str

class QuestionRequest(BaseModel):
    question: str
    history: list[Message]

class SaveMessageRequest(BaseModel):
    session_id: str
    sender: str
    message: str

@app.post("/chat")
async def chat(req: QuestionRequest):
    answer = ask_question(req.question, req.history)
    return {"answer": answer}


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    messages = []
    temp_paths = []

    for file in files:
        temp_path = f"temp_{file.filename}"
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_paths.append(temp_path)
        except Exception as e:
            messages.append(f"❌ {file.filename} lỗi ghi file: {str(e)}")

    try:
        create_vectorstore_from_pdf(temp_paths)
        for path in temp_paths:
            messages.append(f"✅ {os.path.basename(path)} xử lý thành công.")
    except Exception as e:
        messages.append(f"❌ Xử lý lỗi: {str(e)}")
    finally:
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)

    return {"status": "done", "messages": messages}


@app.post("/save-message")
async def save_message(request: SaveMessageRequest, db: Session = Depends(get_db)):
    msg = ChatMessage(session_id=request.session_id, sender=request.sender, message=request.message)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"status": "saved", "id": msg.id}

@app.get("/load-messages")
async def load_messages(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.asc()).all()
    return [
        {"type": msg.sender, "text": msg.message}
        for msg in messages
    ]

@app.get("/list-sessions")
async def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(distinct(ChatMessage.session_id)).all()
    return [session[0] for session in sessions]

#Một API nhỏ dùng để kiểm tra server có đang chạy hay không
@app.get("/health")
async def health_check():
    return {"status": "ok"}

from sqlalchemy import text

@app.get("/db-info")
async def database_info(db: Session = Depends(get_db)):
    try:
        # Lấy thông tin về MySQL server
        version_query = db.execute(text("SELECT VERSION()"))
        version = version_query.scalar()
        
        # Lấy danh sách các bảng trong database hiện tại
        tables_query = db.execute(text("SHOW TABLES"))
        tables = [row[0] for row in tables_query.fetchall()]
        
        return {
            "status": "connected",
            "database_type": "MySQL",
            "version": version,
            "database_name": "chatbot",  # Lấy từ DATABASE_URL của bạn
            "tables": tables
        }
    except Exception as e:
        return {"status": "error", "message": f"Database query failed: {str(e)}"}