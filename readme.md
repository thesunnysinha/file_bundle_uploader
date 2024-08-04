# File Bundle Uploader

This is a FastAPI application for uploading, processing, searching, viewing, and downloading files. The application uses MinIO for object storage, Elasticsearch for searching, and Celery for background processing.

## Features

- Upload ZIP files containing `.pdf`, `.txt`, and `.doc` files.
- Extract and index the content of files for search.
- View and download files from MinIO.
- Search for files based on their content and metadata.

## Requirements

- Python 3.8+
- Docker
- Docker Compose

## Technologies

- **Backend**: FastAPI
- **Search Engine**: Elasticsearch
- **Database**: SQL (SQLAlchemy)
- **File Storage**: Minio
- **Asynchronous Tasks**: Celery
- **Frontend**: HTML, Bootstrap, JavaScript
- **Containerization**: Docker and Docker Compose

## Setup

1. **Clone the repository**

    ```bash
    git clone <repository_url>
    cd file-bundle-uploader
    ```

2. **Create a `.env` file**

    Create a `.env` file in the root directory and add the following environment variables:

    ```env
    DATABASE_URL=postgresql://user:password@db:5432/database
    ELASTICSEARCH_URL=http://elasticsearch:9200
    MINIO_URL=http://minio:9000
    MINIO_ACCESS_KEY=minio
    MINIO_SECRET_KEY=minio123
    MINIO_BUCKET=uploads
    CELERY_BROKER_URL=redis://redis:6379/0
    CELERY_RESULT_BACKEND=redis://redis:6379/0
    ```

3. **Build and start the services**

    ```bash
    docker-compose up --build
    ```

    This command will build the Docker images and start the containers for the FastAPI app, PostgreSQL, Elasticsearch, MinIO, Redis, and Celery worker.

## Endpoints

### Upload a ZIP file

- **URL**: `/upload/`
- **Method**: `PUT`
- **Request**:
    - `file`: The ZIP file to be uploaded.
- **Response**:
    - Renders the upload form with a success or error message.

### Search for files

- **URL**: `/search/`
- **Method**: `GET`
- **Query Parameters**:
    - `q`: The search query.
- **Response**:
    - JSON object containing the search results.

### Download a file

- **URL**: `/download/{obj_storage_id}`
- **Method**: `GET`
- **Path Parameters**:
    - `obj_storage_id`: The ID of the object in MinIO.
- **Response**:
    - The file as a downloadable response.

### View a file

- **URL**: `/view/{obj_storage_id}`
- **Method**: `GET`
- **Path Parameters**:
    - `obj_storage_id`: The ID of the object in MinIO.
- **Response**:
    - Renders the content of the file.

## Project Structure

- `app`: Contains the FastAPI application.
- `config`: Configuration files for the database, Elasticsearch, MinIO, and Celery.
- `models`: SQLAlchemy models.
- `templates`: HTML templates for rendering the upload form and file view.
- `tasks`: Celery tasks for background processing.


## Accessing the Application

**Upload and Search Files**: Navigate to `http://localhost:8000` in your browser to access the file upload and search functionality.

**Check and Explore Minio**: Navigate to `http://localhost:9001` in your browser to access minio console.

### Samples

1. ***File Bundle Uploader***

    ![File Bundle Uploader](./samples/image.png)