from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER=os.getenv("DB_USER")
DB_PASS=os.getenv("DB_PASS")
HOST_NAME=os.getenv("HOST_NAME")
HOST_PORT=os.getenv("HOST_PORT")
DB_NAME=os.getenv("DB_NAME")

# Create DB URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{HOST_NAME}:{HOST_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # testa la connessione prima di usarla
    pool_recycle=1800,       # ricicla le connessioni ogni 30 minuti
    pool_size=5,
    max_overflow=10,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()