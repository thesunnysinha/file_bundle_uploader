import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from models import File
from celery_config import celery_app
from elasticsearch_config import es
from config import DATABASE_URL,LAMBDA_FUNCTION_NAME,AWS_ACCESS_KEY, AWS_SECRET_KEY,S3_BUCKET
import boto3

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def configure_lambda():
    # Initialize Lambda client
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    return lambda_client


@celery_app.task(name='tasks.process_metadata')
def process_metadata(zip_filename):

    lambda_client = configure_lambda()

    # Define payload to pass to Lambda
    payload = {
        "bucket": S3_BUCKET,
        "key": zip_filename
    }

    # Trigger Lambda function
    response = lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    response_payload = json.loads(response['Payload'].read().decode('utf-8'))
    processed_files = response_payload.get('processed_files', [])


    db = SessionLocal()
    try:
        for file in processed_files:
            file_name = file['file_name']
            file_size = file['file_size']
            file_type = file['file_type']
            file_created_date = datetime.now()

            # Save metadata to SQL database
            new_file = File(
                file_name=file_name,
                file_size=file_size,
                file_created_date=file_created_date,
                file_type=file_type,
                source_zip_file_name=zip_filename
            )
            db.add(new_file)
            db.commit()

            # Index document in Elasticsearch
            doc = {
                'file_name': file_name,
                'file_size': file_size,
                'file_created_date': file_created_date,
                'file_type': file_type,
                'source_zip_file_name': zip_filename
            }
            es.index(index="files", doc_type="_doc", body=doc)
    finally:
        db.close()
