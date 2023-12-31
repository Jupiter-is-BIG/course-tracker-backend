import logging
import time
import urllib.request

import requests
from bs4 import BeautifulSoup
from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException,
                     Response, status)
from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..config import settings
from ..models import admin, request, user
from ..utils.db import get_db

router = APIRouter(
    prefix="/scrape",
    tags=["scarpe"],
)


@router.get("/{pwd}")
async def run_engine(pwd: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """ Starts the scraping engine """
    if pwd != settings.admin_pwd:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied",
        )
    
    background_tasks.add_task(scrape_task, db)
    
    return {
        "detail": "Scraping task has been scheduled. It will run in the background.",
    }

def scrape_task(db):
    logging.info("Background task started")
    result = db.query(admin.Admin).filter(admin.Admin.search_active == True).first()
    while result:
        wait_time = (result.frequency)/2
        requested_data = db.query(request.Request).filter(request.Request.is_active == True).all()
        run_user(requested_data, db)
        urllib.request.urlopen("https://course-tracker-backend.onrender.com/").read()
        time.sleep(wait_time)
        urllib.request.urlopen("https://course-tracker-backend.onrender.com/").read()
        time.sleep(wait_time)
        result = db.query(admin.Admin).filter(admin.Admin.search_active == True).first()
    logging.info("Background task Ended")


def sendMessage(token, channel_id, message):
    try:
        url = 'https://discord.com/api/v8/channels/{}/messages'.format(channel_id)
        data = {"content": message}
        header = {"authorization": f"Bot {token}"}
    
        requests.post(url, data=data, headers=header)
    except:
        logging.info(f"Discord DM Sedning Failed for {channel_id}")
 
def createDmChannel(token, user_id):
    try:
        data = {"recipient_id": user_id}
        headers = {"authorization": f"Bot {token}"}
        r = requests.post(f'https://discord.com/api/v9/users/@me/channels', json=data, headers=headers)
    
        channel_id = r.json()['id']
 
        return channel_id
    except:
        logging.info(f"Discord DM Creating Failed for {user_id}")
        return 0

def num_seats(subject: str, code: str, section: str, campus: str):
    url = f'https://courses.students.ubc.ca/cs/courseschedule?tname=subj-section&course={code}&section={section}&campuscd={campus}&dept={subject}&pname=subjarea'
    headers={'User-Agent':'Mozilla/5.0 (Macintosh; PPC Mac OS X 10_8_2) AppleWebKit/531.2 (KHTML, like Gecko) Chrome/26.0.869.0 Safari/531.2'}
    try:
        request_server = requests.get(url, headers=headers)
        webpage = BeautifulSoup(request_server.text, features="lxml")
        return webpage.find('table',class_ = "'table").findAll('strong')[1].text
    except:
        return "0"

def run_user(tracking: list[request.Request], db):
    logging.info("Tracking Now...")
    num_users_notified = 0
    coures_info_text = []
    for course in tracking:
        num = num_seats(course.subject,course.code,course.section,course.campus)
        if (num) != "0":
            interested_users = db.query(user.UserRequests).filter(and_(user.UserRequests.request_id == course.request_id,user.UserRequests.is_active == True)).all()

            if not interested_users:
                course.is_active = False
                db.commit()
                continue
            coures_info_text.append(course.subject + " " + course.code + " " + course.section + " " + course.campus)
            message = f":rocket:  **Attention!!** :rocket:\n\n **{course.subject} {course.code} {course.section}** has **{num} seats available** at the moment.\n You are now being **unsubscribed** for this course.\n If you were *not able to register* in time, please *subscribe again* to keep tracking the availablity."
            
            for discord_user in interested_users:
                discord_user.is_active = False
                try:
                    channel_id = createDmChannel(settings.discord_bot_token, discord_user.user_id)
                    sendMessage(settings.discord_bot_token, channel_id, message)
                    num_users_notified += 1
                except:
                    pass

            course.is_active = False
            db.commit()
            continue

        interested_users = db.query(user.UserRequests).filter(and_(user.UserRequests.request_id == course.request_id,user.UserRequests.is_active == True)).first()

        if not interested_users:
            course.is_active = False
            db.commit()
            continue
    num_info = f"Notified a total of {num_users_notified} users"
    all_course_info = "The following courses were tracked:\n"
    for i in coures_info_text:
        all_course_info = all_course_info + i + "\n"
    logging.info(num_info)
    logging.info(all_course_info)


