#!/bin/bash
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python scripts/refresh_db.py

cd "$script_directory/backend"

alembic revision --autogenerate -m "Initial migration"

alembic upgrade head

uvicorn main:app --reload