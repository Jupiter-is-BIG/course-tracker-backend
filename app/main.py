from fastapi import Depends, FastAPI
from .utils.db import get_db
from sqlalchemy.orm import Session
from .routes import script, scrape, request
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.include_router(script.router)  
app.include_router(scrape.router)
app.include_router(request.router)     


@app.get("/")
async def root(db: Session = Depends(get_db)):
    return {"message": "Course Tracker Backend v0.0.1"}

