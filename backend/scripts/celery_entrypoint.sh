#!/bin/bash

# Function to wait for the backend to be ready
wait_for_backend() {
  scripts/wait-for-it.sh backend:8000 -t 30
}

# Function to wait for the elasticsearch to be ready
wait_for_elasticsearch(){
    scripts/wait-for-it.sh elasticsearch:9200 -t 30
}

# Change the current directory to /code/backend
cd /code/backend

run_celery() {

  celery -A config.celery_config worker --loglevel=info
}

# Execute the wait_for_backend function
wait_for_backend


# Wait for the elastic search
wait_for_elasticsearch

# Execute the run_celery function
run_celery