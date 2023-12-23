from fastapi import APIRouter, Depends, HTTPException, Response, status
from ..models import user, request
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import or_, and_
from ..utils.db import get_db
from ..config import settings
from ..schemas import request_schema

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

@router.get("/login", status_code=200)
async def login(user_name: str, password: str, db: Session = Depends(get_db)):
    """ login route for user """
    auth_search = db.query(user.User).filter(and_(user.User.user_name == user_name, user.User.password == password)).first()
    if not auth_search:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wrong password and username combination"
        )
    
    return {"message" : "Login successful"}


@router.get("/subscriptions", status_code=200, response_model=list[request_schema.Subscription])
async def get_my_subscriptions(user_name: str, password: str, db: Session = Depends(get_db)):
    """ fetch all subscriptions of a user """
    auth_search = db.query(user.User).filter(and_(user.User.user_name == user_name, user.User.password == password)).first()
    if not auth_search:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wrong password and username combination"
        )
    
    all_subs = (
        db.query(request.Request.subject, request.Request.code, request.Request.section, request.Request.campus, request.Request.request_id, user.User.user_id, user.UserRequests.is_active)
        .join(request.Request, request.Request.request_id == user.UserRequests.request_id)
        .join(user.User, user.User.user_id == user.UserRequests.user_id)
        .filter(and_(user.User.user_name == user_name))
        .order_by(user.UserRequests.created_at.desc())
        .all()
    )
  
    return all_subs