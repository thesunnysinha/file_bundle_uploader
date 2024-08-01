from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData
from config.database import Base,engine
from datetime import datetime


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
