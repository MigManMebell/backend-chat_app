import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please create .env file or set it in your hosting provider.")

engine = None
SessionLocal = None

def get_engine():
    global engine
    if engine is None:
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
        except Exception as e:
            print(f"!!! DATABASE CONNECTION FAILED ON CREATE_ENGINE: {e}")
            engine = None # Ensure engine is None if creation fails
    return engine

def get_session_local():
    global SessionLocal
    if SessionLocal is None and get_engine() is not None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal

Base = declarative_base()
