# File Bundle Uploader and Viewer

## Overview

This project is a web application designed to allow users to upload ZIP files containing documents, view file metadata, and search for files based on various attributes. The application is built using FastAPI for the backend, integrates with Elasticsearch for search functionality, and uses Amazon S3 for file storage. Celery is used for asynchronous processing of file metadata.

## Features

- **File Upload**: Upload ZIP files containing documents, which are stored in an Amazon S3 bucket.
- **File Metadata Processing**: Process metadata asynchronously using Celery, storing it in a SQL database and Elasticsearch.
- **Search Functionality**: Search for files by name, type, or source ZIP file name, with results fetched from Elasticsearch.
- **View File Content**: View the content of text files directly in the browser and download files as needed.
- **Download File**: Download files stored in the S3 bucket.

## Technologies

- **Backend**: FastAPI
- **Search Engine**: Elasticsearch
- **Database**: SQL (SQLAlchemy)
- **File Storage**: Amazon S3
- **Asynchronous Tasks**: Celery
- **Frontend**: HTML, Bootstrap, JavaScript
- **Containerization**: Docker and Docker Compose

## Prerequisites

### Install Docker and Docker Compose

#### For Linux

```bash
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

        sudo apt update
        sudo apt install -y docker-ce docker-ce-cli containerd.io
        sudo systemctl enable docker
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        docker-compose --version

    ```

    ## For windows

    Install `Docker Desktop` from docker website.

