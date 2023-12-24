from fastapi import Depends, FastAPI
from .utils.db import get_db
from sqlalchemy.orm import Session
from .routes import script, scrape, request, user
from .models import admin
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.include_router(script.router)  
app.include_router(scrape.router)
app.include_router(request.router)   
app.include_router(user.router)   

@app.get("/")
async def root():
    return {"message": "Course Tracker Backend v0.0.1"}