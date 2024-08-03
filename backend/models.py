from sqlalchemy import Column, Integer, String, DateTime, Text
from config.database import Base

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    file_size = Column(Integer)
    file_created_date = Column(DateTime)
    file_type = Column(String)
    source_zip_file_name = Column(String)
    obj_storage_id = Column(String)
    content = Column(Text)
