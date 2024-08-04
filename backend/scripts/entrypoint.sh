#!/bin/bash

# Function to wait for the database to be ready
wait_for_database() {
  scripts/wait-for-it.sh db:5432 -t 5
}

# Function to wait for the elasticsearch to be ready
wait_for_elasticsearch(){
    scripts/wait-for-it.sh elasticsearch:9200 -t 5
}

# Function to wait for the minio to be ready
wait_for_minio(){
    scripts/wait-for-it.sh minio:9000 -t 5
}

# Change the current directory to /code/backend
cd /code/backend

# Function to run the application
run_application() {
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

# Wait for the database
wait_for_database

# Wait for the elastic search
wait_for_elasticsearch

# Wait for the minio
wait_for_minio

# Run the application
run_application