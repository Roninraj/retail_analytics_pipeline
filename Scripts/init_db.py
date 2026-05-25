import os
from backend.models import Base
from backend.database import engine

def init_db():
    print(f"Connecting to database to initialize schema...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database schema initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
