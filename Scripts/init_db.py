import os
from sqlalchemy import create_engine
from backend.models import Base
from backend.database import SQLALCHEMY_DATABASE_URL

def init_db():
    print(f"Connecting to database to initialize schema...")
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("Database schema initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
