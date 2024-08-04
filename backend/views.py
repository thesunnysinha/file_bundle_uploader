import io
import mimetypes
from fastapi import APIRouter, Request, UploadFile, Query, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from config.celery_config import celery_app
from config.config import templates, MINIO_BUCKET
from config.elasticsearch_config import es
from config.minio_config import minio_client
from minio.error import S3Error
from config.database import db_dependency
from models.files import Files

class UploadView:
    def __init__(self):
        # Register API routes
        self.router = APIRouter()
        self.router.add_api_route("/", self.get_upload_form, methods=["GET"], response_class=HTMLResponse)
        self.router.add_api_route("/upload/", self.upload_zipfile, methods=["PUT"], response_class=JSONResponse)
        self.router.add_api_route("/search/", self.search_files, methods=["GET"], response_class=JSONResponse)
        self.router.add_api_route("/download/{obj_storage_id}", self.download_file, methods=["GET"])
        self.router.add_api_route("/view/{obj_storage_id}", self.view_file_content, methods=["GET"])

    async def get_upload_form(self, request: Request):
        return templates.TemplateResponse("upload.html", {"request": request})

    async def upload_zipfile(self, file: UploadFile = File(...)):
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

        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

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
            "file_name": hit["_source"].get("file_name"),
            "file_type": hit["_source"].get("file_type"),
            "file_size": hit["_source"].get("file_size"),
            "source_zip_file_name": hit["_source"].get("source_zip_file_name"),
            "obj_storage_id": hit["_source"].get("obj_storage_id"),
            "content": hit["_source"].get("content")
        } for hit in hits]

        return JSONResponse({"files": results}, status_code=200)

    async def download_file(self, obj_storage_id: str, db: db_dependency):
        try:
            # Try to get the file information from the database
            file_info = db.query(Files).filter(Files.obj_storage_id == obj_storage_id).first()

            if file_info:
                filename = file_info.file_name
                content_type = file_info.file_type
            else:
                # Fallback to the existing method if file is not found in the database
                stat = minio_client.stat_object(MINIO_BUCKET, obj_storage_id)
                filename = stat.metadata.get("X-Amz-Meta-Filename", obj_storage_id)
                content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

            # Get the object from MinIO
            response = minio_client.get_object(MINIO_BUCKET, obj_storage_id)

            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': content_type
            }

            return StreamingResponse(response, media_type=content_type, headers=headers)
        except S3Error as err:
            raise HTTPException(status_code=500, detail="Failed to download file") from err

    async def view_file_content(self, obj_storage_id: str):
        try:
            # Ensure obj_storage_id is a string
            obj_storage_id = str(obj_storage_id)

            # Query Elasticsearch for file content using obj_storage_id
            search_body = {
                "query": {
                    "match": {
                        "obj_storage_id": obj_storage_id
                    }
                }
            }

            response = es.search(index="files", body=search_body)

            if response['hits']['hits']:
                file_content = response['hits']['hits'][0]['_source'].get('content', 'No content available')
                return {"file_content": file_content}
            else:
                raise HTTPException(status_code=404, detail="File not found in Elasticsearch")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to serialize to JSON: {e}")
