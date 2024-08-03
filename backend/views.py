import io
from fastapi import APIRouter, Request, UploadFile, File, Query, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
import boto3
from botocore.exceptions import NoCredentialsError
from config.celery_config import celery_app
from config.config import S3_BUCKET, AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_FINAL_BUCKET, templates
from config.elasticsearch_config import es
from main import db_dependency

class UploadView:
    def __init__(self):
        # Register API routes
        self.router = APIRouter()
        self.router.add_api_route("/", self.get_upload_form, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/upload/", self.upload_zipfile, methods=["POST"], response_class=HTMLResponse)
        self.router.add_api_route("/upload/", self.upload_zipfile_put, methods=["PUT"], response_class=JSONResponse)
        self.router.add_api_route("/search/", self.search_files, methods=["GET"], response_class=JSONResponse)
        self.router.add_api_route("/download/{file_name}", self.download_file, methods=["GET"])
        
    async def get_upload_form(self, request: Request):
        return templates.TemplateResponse("upload.html", {"request": request})

    async def upload_zipfile_put(self, request: Request, file: UploadFile = FastAPIFile(...), db: db_dependency):
        permitted_types = ["application/zip", "application/x-zip-compressed"]
        if file.content_type not in permitted_types:
            return JSONResponse({"error": "Invalid file type. Only zip files are allowed."}, status_code=400)

        try:
            zip_filename = file.filename
            zip_data = file.file.read()
            file_stream = io.BytesIO(zip_data)

            # Upload ZIP file to MinIO
            minio_client.put_object(
                MINIO_BUCKET,
                zip_filename,
                file_stream,
                length=len(zip_data)
            )

            # Trigger Celery task for post-processing
            celery_app.send_task('tasks.process_metadata', args=[zip_filename])

        except NoCredentialsError:
            return JSONResponse({"error": "Credentials not available"}, status_code=500)

        return JSONResponse({"message": "File uploaded and processed successfully."}, status_code=200)
    
    async def search_files(self, q: str = Query(None)):
        if not q:
            query_body = {
                "query": {
                    "match_all": {}
                }
            }
        else:
            query_body = {
                "query": {
                    "query_string": {
                        "query": f"*{q}*",
                        "fields": ["file_name", "file_type", "source_zip_file_name", "content"]
                    }
                }
            }

        # Check if the index exists
        if not es.indices.exists(index="files"):
            return JSONResponse({"error": "No data available to show."}, status_code=500)

        # Perform the search query
        res = es.search(index="files", body=query_body)

        # Extract hits
        hits = res['hits']['hits']

        if not hits:
            return JSONResponse({"message": "No matches found."}, status_code=200)

        # Prepare the response with the required fields
        results = [{
            "file_name": hit["_source"]["file_name"],
            "file_type": hit["_source"]["file_type"],
            "file_size": hit["_source"]["file_size"],
            "source_zip_file_name": hit["_source"]["source_zip_file_name"],
            "obj_storage_id": hit["_source"]["obj_storage_id"]
        } for hit in hits]

        return JSONResponse({"files": results}, status_code=200)
            
    async def download_file(self, file_name: str):
        file_obj = minio_client.get_object(MINIO_BUCKET, file_name)
        return FileResponse(file_obj, media_type='application/octet-stream', filename=file_name)


    # async def view_file(self, request: Request, file_name: str):
    #     s3_client = configure_s3()
    #     try:
    #         file_obj = s3_client.get_object(Bucket=S3_FINAL_BUCKET, Key=file_name)
    #         content_type = file_obj.get('ContentType', 'application/octet-stream')
    #         file_body = file_obj['Body'].read()

    #         content_disposition = 'inline'
    #         if 'text' in content_type:
    #             content = file_body.decode('utf-8', errors='replace')
    #             return templates.TemplateResponse("view_file.html", {"request": request, "file_name": file_name, "content": content})

    #         return StreamingResponse(
    #             io.BytesIO(file_body),
    #             media_type=content_type,
    #             headers={"Content-Disposition": f"{content_disposition}; filename={file_name}"}
    #         )

    #     except s3_client.exceptions.NoSuchKey:
    #         raise HTTPException(status_code=404, detail="File not found")
    #     except NoCredentialsError:
    #         raise HTTPException(status_code=403, detail="Credentials not available")