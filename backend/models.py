from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
from config import DATABASE_URL

# Load environment variables from .env file
load_dotenv()

# Set up SQLAlchemy
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    file_size = Column(Integer)
    file_created_date = Column(DateTime, default=datetime.utcnow)
    file_type = Column(String)
    source_zip_file_name = Column(String)

# Create all tables in the database
def init_db():
    Base.metadata.create_all(bind=engine)
