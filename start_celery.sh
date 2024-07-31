#!/bin/bash
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


cd "$script_directory/backend"

celery -A celery_config.celery_app worker --loglevel=info
