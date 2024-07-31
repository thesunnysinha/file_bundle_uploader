from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from models import init_db
import uvicorn
from urls import router

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Initialize FastAPI app
app = FastAPI()

# Initialize the database
init_db()

# Import and include the router from urls
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
