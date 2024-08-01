from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.templating import Jinja2Templates
import uvicorn
from urls import router
from models import init_db
from config.database import engine,SessionLocal
from sqlalchemy.orm import Session

# Initialize FastAPI app
app = FastAPI()

# Initialize the database
init_db()

# Import and include the router from urls
app.include_router(router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
