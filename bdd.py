import os
from sqlmodel import create_engine, SQLModel
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.getenv('DB_SERVER')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DRIVER = os.getenv('DRIVER')

SQL_DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver={DRIVER}"

engine = create_engine(SQL_DATABASE_URL, echo=True)
