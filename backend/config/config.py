import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

# AWS
S3_BUCKET = os.getenv("S3_BUCKET")
S3_FINAL_BUCKET = os.getenv("S3_FINAL_BUCKET")

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION= os.getenv("AWS_REGION")

#LAMBDA
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME")

# Database
DATABASE_URL = os.getenv("SQL_DATABASE_URL")

#Redis
REDIS_URL = os.getenv("REDIS_URL")

#Elasticsearch
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Mount the static files directory
static = StaticFiles(directory="static")