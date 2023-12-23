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
async def root(db: Session = Depends(get_db)):
    admin_init = db.query(admin.Admin).first()
    if not admin_init:
        new_admin = admin.Admin(
            search_active = True,
            frequency = 600,
        )
        db.add(new_admin)
        db.commit()
    return {"message": "Course Tracker Backend v0.0.1"}

