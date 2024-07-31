import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates

load_dotenv()

# Configuration
S3_BUCKET = os.getenv("S3_BUCKET")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME")
DATABASE_URL = os.getenv("SQL_DATABASE_URL")


# Initialize templates
templates = Jinja2Templates(directory="templates")