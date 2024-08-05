from config.minio_config import minio_client, MINIO_BUCKET
from config.celery_config import celery_app
from utils import unzip_push_to_db_bucket


@celery_app.task(name='tasks.process_metadata')
def process_metadata(zip_filename):
    try:
        # Step 1: Get ZIP file from MinIO
        try:
            zip_data = minio_client.get_object(MINIO_BUCKET, zip_filename)
            print(f"Successfully retrieved ZIP file: {zip_filename}")
        except Exception as e:
            print(f"Error retrieving ZIP file from MinIO: {e}")
            return

        # Step 2: Unzip and push to DB and MinIO
        try:
            unzip_push_to_db_bucket(zip_data, zip_filename)
            print(f"Successfully processed ZIP file: {zip_filename}")
        except Exception as e:
            print(f"Error unzipping and pushing to DB/MinIO: {e}")
            return

        # Step 3: Delete the ZIP file from MinIO
        try:
            minio_client.remove_object(MINIO_BUCKET, zip_filename)
            print(f"Successfully deleted ZIP file from MinIO: {zip_filename}")
        except Exception as e:
            print(f"Error deleting ZIP file from MinIO: {e}")
            return 

    except Exception as e:
        print(f"Error processing ZIP file: {e}")

