from fastapi import Depends, FastAPI
from .utils.db import get_db
from sqlalchemy.orm import Session


app = FastAPI()

@app.get("/")
async def root(db: Session = Depends(get_db)):
    return {"message": "Virtual Card Backend v0.0.1"}