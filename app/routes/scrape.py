from fastapi import APIRouter, Depends, HTTPException, Response, status
from ..models import admin, request
from sqlalchemy.orm import Session
from ..utils.db import get_db
from ..config import settings
import requests
from bs4 import BeautifulSoup
import time
from fastapi import BackgroundTasks
import logging


router = APIRouter(
    prefix="/scrape",
    tags=["scarpe"],
)


MY_DEVICE = "erj0IBWATQaaq0wAvND29Z:APA91bFpzckb2kws9XoVYsgWvxrBxuyM4ceChV4rpBlSLa-vTge4yl2aTAS996tywqhbn9RGkuRozPS5OyP43WWnfdEH7yb_E9LnwnsDj4veWbfhtStXOKXG9QlBJJwnya_mBu9JLmsa"
def sendNotification(courseName, token):
    return {
        "priority": "high",
        "data": {
            "title": "URGENT",
            "detail": f"A seat is now available in {courseName}!!"
        },
        "to": token
    }
    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": "key=AAAA29jy38c:APA91bG5LN-Av5wblW9rUIfRcgJ9DPQ_yyrP0dKxha_Anw-bFtwi6Ze-mUnnSs1ozYtXSEtr2ccdRB1fsCYI6avPzL_bHO3LlBYPwbsQVuUsCyeURTPFoyC-albkG77kGEsqWI23nkMN"
    # }
    # response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, json=json)
    # print(response.status_code)

def num_seats(subject: str, code: str, section: str, campus: str):
    url = f'https://courses.students.ubc.ca/cs/courseschedule?tname=subj-section&course={code}&section={section}&campuscd={campus}&dept={subject}&pname=subjarea'
    headers={'User-Agent':'Mozilla/5.0 (Macintosh; PPC Mac OS X 10_8_2) AppleWebKit/531.2 (KHTML, like Gecko) Chrome/26.0.869.0 Safari/531.2'}
    request = requests.get(url, headers=headers)
    webpage = BeautifulSoup(request.text, features="lxml")
    return webpage.find('table',class_ = "'table").findAll('strong')[1].text

def run_user(token: str, tracking: list[request.Request], i: int):
    msg = ""
    for course in tracking:
        num = num_seats(course.subject,course.code,course.section,course.campus)
        if (num) != "0":
            msg+=course.subject + course.code + f"({num}), "
    if msg!= "":
        # sendNotification(msg, token)
        print(f"Ping {i}: {msg}")
    else:
        print(f"Ping {i}: Nothing available!")

def scrape_task(requested_data, db):
    print("Background task started")
    i = 1
    result = db.query(admin.Admin).filter(admin.Admin.search_active == True).first()
    while result:   
        run_user(MY_DEVICE, requested_data, i)
        i += 1
        time.sleep(result.frequency)
        if i % 3 == 0:
            result = db.query(admin.Admin).filter(admin.Admin.search_active == True).first()
    print("Background task ended")

@router.get("/{pwd}")
async def run_engine(pwd: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """ Starts the scraping engine """
    if pwd != settings.admin_pwd:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied",
        )
    
    requested_data = db.query(request.Request).filter(request.Request.is_active == True).all()
    background_tasks.add_task(scrape_task, requested_data, db)
    
    return {
        "detail": "Scraping task has been scheduled. It will run in the background.",
    }
