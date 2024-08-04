import io
import zipfile
from datetime import datetime
from minio.error import S3Error
from config.minio_config import minio_client, MINIO_BUCKET
from config.elasticsearch_config import es
from models.files import Files
from config.database import SessionLocal
from sqlalchemy.orm import Session
import PyPDF2
import docx
from config.celery_config import celery_app
import uuid

# Helper functions to process different file types
def process_text_file(file_content):
    return file_content.decode('utf-8')

def process_pdf_file(file_content):
    content = ""
    with io.BytesIO(file_content) as pdf_file:
        reader = PyPDF2.PdfFileReader(pdf_file)
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            content += page.extract_text()
    return content

def process_doc_file(file_content):
    content = ""
    with io.BytesIO(file_content) as doc_file:
        doc = docx.Document(doc_file)
        for para in doc.paragraphs:
            content += para.text
    return content

@celery_app.task(name='tasks.process_metadata')
def process_metadata(zip_filename):
    try:
        # Get ZIP file from MinIO
        zip_data = minio_client.get_object(MINIO_BUCKET, zip_filename)

        # Initialize a variable to track the processed size
        total_size = 0
        chunk_size = 128 * 1024 * 1024  # 128 MB

        # Create a BytesIO buffer to hold chunks of the ZIP file
        buffer = io.BytesIO()
        
        db: Session = SessionLocal()
        
        try:

            for chunk in zip_data.stream(16 * 1024):  # 16 KB chunks
                buffer.write(chunk)
                total_size += len(chunk)

                if total_size >= chunk_size:
                    buffer.seek(0)
                    with zipfile.ZipFile(buffer, 'r') as zip_file:
                        for file_info in zip_file.infolist():
                            if file_info.filename.endswith(('.pdf', '.txt', '.doc')):
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
                                    elif file_type == 'doc':
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
                        if file_info.filename.endswith(('.pdf', '.txt', '.doc')):
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
                                elif file_type == 'doc':
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

            # Delete the ZIP file from MinIO
            minio_client.remove_object(MINIO_BUCKET, zip_filename)

        finally:
            db.close()
    except S3Error as e:
        print(f"Error processing ZIP file: {e}")
