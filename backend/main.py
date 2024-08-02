from typing import Annotated
from fastapi import Depends, FastAPI
import uvicorn
from urls import router
from config.database import init_db, SessionLocal
from sqlalchemy.orm import Session
from config.config import static

# Initialize FastAPI app
app = FastAPI()

# Initialize the database
init_db()

# Import and include the router from urls
app.include_router(router)

app.mount("/static", static, name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
