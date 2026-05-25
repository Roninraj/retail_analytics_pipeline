import os
import pandas as pd
from sqlalchemy import create_engine
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ingest_data():
    # Configuration from environment variables
    db_user = os.getenv('DB_USER', 'retail_user')
    db_password = os.getenv('DB_PASSWORD', 'retail_password')
    db_host = os.getenv('DB_HOST', 'mysql-service')
    db_name = os.getenv('DB_NAME', 'retail_db')
    file_path = os.getenv('DATASET_PATH', 'Dataset/online_retail_II.xlsx')

    connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    
    try:
        engine = create_engine(connection_string)
        logger.info(f"Connected to database at {db_host}")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        sys.exit(1)

    if not os.path.exists(file_path):
        logger.error(f"Dataset file not found at {file_path}")
        sys.exit(1)

    try:
        logger.info(f"Reading dataset from {file_path}...")
        xl = pd.ExcelFile(file_path)
        
        with engine.begin() as connection:
            for sheet_name in xl.sheet_names:
                logger.info(f"Processing sheet: {sheet_name}")
                df = xl.parse(sheet_name)
                
                # Basic cleaning: rename columns to be SQL friendly
                df.columns = [c.replace(' ', '_').lower() for c in df.columns]
                
                # Write to MySQL
                logger.info(f"Writing {len(df)} rows from {sheet_name} to table 'raw_transactions'...")
                df.to_sql('raw_transactions', con=connection, if_exists='append', index=False)
            
        logger.info("Ingestion completed successfully.")
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ingest_data()
