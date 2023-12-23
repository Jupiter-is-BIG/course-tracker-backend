from fastapi import APIRouter, Depends, HTTPException, Response, status
from ..models import user
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..utils.db import get_db
from ..config import settings

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post("/", status_code=201)
async def create_user(user_id: str, user_name: str, password: str, db: Session = Depends(get_db)):
    """ Creates new user account """
    pre_search = db.query(user.User).filter(or_(user.User.user_id == user_id, user.User.user_name == user_name)).first()
    if pre_search:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists with this username or discord",
        )
    
    new_user = user.User(
        user_id = user_id,
        user_name = user_name,
        password = password
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}



