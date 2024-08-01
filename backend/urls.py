from fastapi import APIRouter
from views import UploadView

upload_view = UploadView()
router = APIRouter()

# Include the router from the UploadView class
router.include_router(upload_view.router)
