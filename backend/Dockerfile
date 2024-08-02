FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY requirements.txt /tmp/requirements.txt

# Create a virtual environment
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp

# Activate the virtual environment
ENV PATH="/venv/bin:$PATH"

COPY . /code/backend/

WORKDIR /code/backend

RUN chmod +x scripts/wait-for-it.sh scripts/entrypoint.sh scripts/celery_entrypoint.sh

# Specify the entrypoint script
ENTRYPOINT ["scripts/entrypoint.sh"]
    