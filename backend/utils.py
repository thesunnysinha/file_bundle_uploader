import io
import zipfile
from datetime import datetime
from config.database import SessionLocal
import uuid
from models.files import Files
from config.elasticsearch_config import es
import PyPDF2
import docx
from config.minio_config import minio_client
from config.config import MINIO_BUCKET
from sqlalchemy.orm import Session

def process_text_file(file_content):
    return file_content.decode('utf-8')

def process_pdf_file(file_content):
    content = ""
    with io.BytesIO(file_content) as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            content += page.extract_text()
    return content

def process_doc_file(file_content):
    content = ""
    with io.BytesIO(file_content) as doc_file:
        doc = docx.Document(doc_file)
        for para in doc.paragraphs:
            content += para.text
    return content

def unzip_push_to_db_bucket(zip_data,zip_filename):
    db: Session = SessionLocal()
    try:
        # Initialize a variable to track the processed size
        total_size = 0
        chunk_size = 128 * 1024 * 1024  # 128 MB

        # Create a BytesIO buffer to hold chunks of the ZIP file
        buffer = io.BytesIO()
        

        for chunk in zip_data.stream(16 * 1024):  # 16 KB chunks
            buffer.write(chunk)
            total_size += len(chunk)

            if total_size >= chunk_size:
                buffer.seek(0)
                with zipfile.ZipFile(buffer, 'r') as zip_file:
                    for file_info in zip_file.infolist():
                        if file_info.filename.endswith(('.pdf', '.txt', '.doc','.docx')):
                            with zip_file.open(file_info) as file:
                                file_name = file_info.filename
                                file_content = file.read()
                                file_size = len(file_content)
                                file_type = file_info.filename.split('.')[-1].lower()

                                # Process content based on file type
                                if file_type == 'txt':
                                    content = process_text_file(file_content)
                                elif file_type == 'pdf':
                                    content = process_pdf_file(file_content)
                                elif file_type == 'doc' or file_type == 'docx':
                                    content = process_doc_file(file_content)
                                else:
                                    continue

                                # Ensure content is not None or empty
                                content = content.strip() if content else None

                                # Upload file to MinIO
                                obj_storage_id = str(uuid.uuid4())
                                minio_client.put_object(
                                    MINIO_BUCKET,
                                    obj_storage_id,
                                    io.BytesIO(file_content),
                                    file_size,
                                    content_type="application/octet-stream"
                                )

                                # Save metadata to SQL database
                                new_file = Files(
                                    file_name=file_name,
                                    file_size=file_size,
                                    file_created_date=datetime.now(),
                                    file_type=file_type,
                                    source_zip_file_name=zip_filename,
                                    obj_storage_id=obj_storage_id
                                )
                                try:
                                    db.add(new_file)
                                    db.commit()
                                    print(f"Saved to database: {new_file}")
                                except Exception as e:
                                    db.rollback()
                                    print(f"Failed to save to database: {e}")

                                # Index document in Elasticsearch
                                doc = {
                                    'file_name': file_name,
                                    'file_size': file_size,
                                    'file_created_date': datetime.now(),
                                    'file_type': file_type,
                                    'source_zip_file_name': zip_filename,
                                    'obj_storage_id':obj_storage_id,
                                    'content': content
                                }
                                
                                print(f"doc --> {doc}")
                                es.index(index="files", body=doc)

                # Reset buffer and total size after processing
                buffer = io.BytesIO()
                total_size = 0

        # Clean up any remaining data in the buffer
        if total_size > 0:
            buffer.seek(0)
            with zipfile.ZipFile(buffer, 'r') as zip_file:
                for file_info in zip_file.infolist():
                    if file_info.filename.endswith(('.pdf', '.txt', '.doc','.docx')):
                        with zip_file.open(file_info) as file:
                            file_name = file_info.filename
                            file_content = file.read()
                            file_size = len(file_content)
                            file_type = file_info.filename.split('.')[-1].lower()

                            # Process content based on file type
                            if file_type == 'txt':
                                content = process_text_file(file_content)
                            elif file_type == 'pdf':
                                content = process_pdf_file(file_content)
                            elif file_type == 'doc' or file_type =='docx':
                                content = process_doc_file(file_content)
                            else:
                                continue

                            # Ensure content is not None or empty
                            content = content.strip() if content else None

                            # Upload file to MinIO
                            obj_storage_id = str(uuid.uuid4())
                            minio_client.put_object(
                                MINIO_BUCKET,
                                obj_storage_id,
                                io.BytesIO(file_content),
                                file_size,
                                content_type="application/octet-stream"
                            )

                            # Save metadata to SQL database
                            new_file = Files(
                                file_name=file_name,
                                file_size=file_size,
                                file_created_date=datetime.now(),
                                file_type=file_type,
                                source_zip_file_name=zip_filename,
                                obj_storage_id=obj_storage_id
                            )
                            
                            try:
                                db.add(new_file)
                                db.commit()
                                print(f"Saved to database: {new_file}")
                            except Exception as e:
                                db.rollback()
                                print(f"Failed to save to database: {e}")

                            # Index document in Elasticsearch
                            doc = {
                                'file_name': file_name,
                                'file_size': file_size,
                                'file_created_date': datetime.now(),
                                'file_type': file_type,
                                'source_zip_file_name': zip_filename,
                                'obj_storage_id':obj_storage_id,
                                'content': content
                            }
                            
                            print(f"doc --> {doc}")
                            es.index(index="files", body=doc)
    finally:
        db.close()