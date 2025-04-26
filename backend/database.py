from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load biến môi trường từ .env
load_dotenv()

# Lấy từng biến
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Build DATABASE_URL chuẩn
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Nếu thiếu bất kỳ biến nào thì raise lỗi luôn cho chắc
required_vars = [DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME]
if any(var is None for var in required_vars):
    raise ValueError("Thiếu biến môi trường kết nối database!")

# Kết nối
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
