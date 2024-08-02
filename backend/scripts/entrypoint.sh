#!/bin/bash

# Function to wait for the database to be ready
wait_for_database() {
  scripts/wait-for-it.sh db:5432 -t 30
}

# Function to wait for the elasticsearch to be ready
wait_for_elasticsearch(){
    scripts/wait-for-it.sh elasticsearch:9200 -t 30
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

# Run the application
run_application