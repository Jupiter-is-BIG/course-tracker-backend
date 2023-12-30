from fastapi import Depends, FastAPI
from .utils.db import get_db
from sqlalchemy.orm import Session
from .routes import script, scrape, request, user
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

origins = [
    "https://course-tracker-backend.onrender.com",
    "https://course-tracker-frontend-kappa.vercel.app/",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(script.router)  
app.include_router(scrape.router)
app.include_router(request.router)   
app.include_router(user.router)   

@app.get("/")
async def root():
    return {"message": "Course Tracker Backend v0.0.1"}