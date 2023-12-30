from fastapi import APIRouter, Depends, HTTPException, Response, status
from ..models import request, user
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..utils.db import get_db
from datetime import datetime
from hashlib import sha256
from bs4 import BeautifulSoup
from .scrape import sendMessage, createDmChannel
from ..config import settings
import requests
import logging


router = APIRouter(
    prefix="/request",
    tags=["request"],
)

@router.post("/", status_code=201)
async def push_request(
    user_name: str,
    password: str,
    subject: str,
    code: str,
    section: str,
    campus: str,
    db: Session = Depends(get_db)
):
    """ Pushes new tracking requests """
    password = sha256(password.encode('utf-8')).hexdigest()
    current_user = db.query(user.User).filter(user.User.user_name == user_name).first()
    if (not current_user) or current_user.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
        )
    
    num_of_existsing_requests = (
        db.query(user.UserRequests)
        .filter(and_(user.UserRequests.user_id == current_user.user_id, user.UserRequests.is_active == True))
        .count()
    )

    if num_of_existsing_requests and num_of_existsing_requests >= 4:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Already at max limit for course tracking",
        )

    
    if not (subject and code and section and campus):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Wrong format",
        )
    
    if (len(subject) != 4 or len(code) != 3 or len(section) != 3 or len(campus) != 4):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Wrong format",
        )
    
    url = f'https://courses.students.ubc.ca/cs/courseschedule?tname=subj-section&course={code}&section={section}&campuscd={campus}&dept={subject}&pname=subjarea'
    headers={'User-Agent':'Mozilla/5.0 (Macintosh; PPC Mac OS X 10_8_2) AppleWebKit/531.2 (KHTML, like Gecko) Chrome/26.0.869.0 Safari/531.2'}
    try:
        request_server = requests.get(url, headers=headers)
        webpage = BeautifulSoup(request_server.text, features="lxml")
        webpage.find('table',class_ = "'table").findAll('strong')[1].text
    except:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No such course exists",
        )
    
    dive = db.query(request.Request).filter(and_(request.Request.subject == subject,request.Request.code == code,request.Request.section == section,request.Request.campus == campus)).first()
    
    if dive:
        previous_record = db.query(user.UserRequests).filter(and_(user.UserRequests.user_id == current_user.user_id,user.UserRequests.request_id == dive.request_id)).first()
        
        if previous_record:
            previous_record.is_active = True
            previous_record.created_at = datetime.now()
        else:
            new_record = user.UserRequests(
                user_id = current_user.user_id,
                request_id = dive.request_id,
                is_active = True
            )
            db.add(new_record)
        
        
        dive.is_active = True
        db.commit()
        
        message_confirmation = f"Hey {user_name}! We are now tracking {subject} {code} {section} of {campus} for you! :saluting_face:\n We will send you a DM on discord when we see a seat available :)\n\n Please note that we look for seat availablity every 20 minutes to avoid any load on UBC servers, respecting [UBC Terms of Use Section F](https://www.ubc.ca/site/legal.html)."
        channel_id = createDmChannel(settings.discord_bot_token, current_user.user_id)
        sendMessage(settings.discord_bot_token, channel_id, message_confirmation)

        return {"message": f"Resquest for {subject} {code} {section} on {campus} campus has been registered successfully"}
    
        
    new_request = request.Request(
        subject=subject,
        code=code,
        section=section,
        campus=campus
    )

    db.add(new_request)
    db.commit()

    new_record = user.UserRequests(
        user_id = current_user.user_id,
        request_id = new_request.request_id,
        is_active = True
    )
    db.add(new_record)
    db.commit()

    message_confirmation = f"Hey {user_name}! We are now tracking {subject} {code} {section} of {campus} for you! :saluting_face:\n We will send you a DM on discord when we see a seat available :)\n\n Please note that we look for seat availablity every 20 minutes to avoid any load on UBC servers, respecting [UBC Terms of Use Section F](https://www.ubc.ca/site/legal.html)."
    channel_id = createDmChannel(settings.discord_bot_token, current_user.user_id)
    sendMessage(settings.discord_bot_token, channel_id, message_confirmation)

    return {"message": f"Resquest for {subject} {code} {section} on {campus} campus has been registered successfully"}

