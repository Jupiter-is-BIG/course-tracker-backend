from fastapi import APIRouter, Depends, HTTPException, Response, status
from ..models import user, request
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from ..utils.db import get_db
from ..config import settings
from ..schemas import request_schema
from hashlib import sha256
import requests
from .scrape import sendMessage, createDmChannel

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

    headers = {
        "Authorization": f"Bot {settings.discord_bot_token}",
        "User-Agent": "myBotThing (http://some.url, v0.1)",
    }
    url = f"https://discordapp.com/api/users/{user_id}"
    try:
        response = requests.get(url, headers=headers)    
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Wrong Discord User Id",
            )
    except:
        raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Wrong Discord User Id",
            )
    
    new_user = user.User(
        user_id = user_id,
        user_name = user_name,
        password = sha256(password.encode('utf-8')).hexdigest()
    )

    db.add(new_user)
    db.commit()

    message_confirmation = f"Hey {user_name}! Thanks for registering your account on course tracker :D You can now start tracking courses!"
    channel_id = createDmChannel(settings.discord_bot_token, user_id)
    sendMessage(settings.discord_bot_token, channel_id, message_confirmation)

    return {"message": "User registered successfully"}

@router.get("/login", status_code=200)
async def login(user_name: str, password: str, db: Session = Depends(get_db)):
    """ login route for user """
    password = sha256(password.encode('utf-8')).hexdigest()
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
    password = sha256(password.encode('utf-8')).hexdigest()
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

@router.delete("subscriptions", status_code=200)
async def delete_subscription(user_name: str, password: str, request_id: str, db: Session = Depends(get_db)):
    """ delete my subscription """
    password = sha256(password.encode('utf-8')).hexdigest()
    cur_user = db.query(user.User).filter(and_(user.User.user_name == user_name, user.User.password == password)).first()
    if not cur_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wrong password and username combination"
        )
    
    request_verification = db.query(user.UserRequests).filter(and_(user.UserRequests.user_id == cur_user.user_id, user.UserRequests.request_id == request_id)).first()
    if not request_verification:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are linked to any such course"
        )
    
    db.delete(request_verification)
    db.commit()

    return {"message" : "Deleted course link successfully"}