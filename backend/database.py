import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_user = os.getenv('DB_USER', 'retail_user')
db_password = os.getenv('DB_PASSWORD', 'retail_password')
db_host = os.getenv('DB_HOST', 'mysql-service')
db_name = os.getenv('DB_NAME', 'retail_db')

# Industrial DB Connection String with Pooling
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

db_ssl_mode = os.getenv('DB_SSL_MODE', 'PREFERRED')
connect_args = {}
if db_ssl_mode:
    connect_args["ssl"] = {"ssl_mode": db_ssl_mode}

# pool_size: number of permanent connections
# max_overflow: number of temporary connections beyond pool_size
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
