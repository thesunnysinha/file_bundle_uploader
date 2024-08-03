from minio import Minio
from .config import MINIO_ACCESS_KEY,MINIO_BUCKET,MINIO_ENDPOINT,MINIO_SECRET_KEY

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)


found = minio_client.bucket_exists(MINIO_BUCKET)
if not found:
    minio_client.make_bucket(MINIO_BUCKET)
