from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse
import boto3
from botocore.exceptions import NoCredentialsError
from config.celery_config import celery_app
from config.config import S3_BUCKET, AWS_ACCESS_KEY, AWS_SECRET_KEY,templates

def configure_s3():
    s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY
            )
    
    return s3_client


class UploadView:
    def __init__(self):
        # Register API routes
        self.router = APIRouter()
        self.router.add_api_route("/", self.get_upload_form, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/upload/", self.upload_zipfile, methods=["POST"], response_class=HTMLResponse)

    async def get_upload_form(self, request: Request):
        return templates.TemplateResponse("upload.html", {"request": request})

    async def upload_zipfile(self, request: Request, file: UploadFile = File(...)):
        print(file.content_type)

        permitted_types = ["application/zip", "application/x-zip-compressed"]
        if file.content_type not in permitted_types:
            return templates.TemplateResponse("upload.html", {"request": request, "error": "Invalid file type. Only zip files are allowed."})

        try:
            zip_filename = file.filename
            s3_client = configure_s3()
            s3_client.upload_fileobj(file.file, S3_BUCKET, zip_filename)
            
            # Trigger Celery task for post-processing
            celery_app.send_task('tasks.process_metadata', args=[zip_filename])

        except NoCredentialsError:
            return templates.TemplateResponse("upload.html", {"request": request, "error": "Credentials not available"})

        return templates.TemplateResponse("upload.html", {"request": request, "message": "File uploaded successfully. Processing in background."})

upload_view = UploadView()
