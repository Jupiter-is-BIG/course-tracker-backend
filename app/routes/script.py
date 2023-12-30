from fastapi import APIRouter, Depends, HTTPException, Response, status
from ..models import admin
from sqlalchemy.orm import Session
from ..utils.db import get_db
from ..config import settings
import requests
from bs4 import BeautifulSoup
import logging

router = APIRouter(
    prefix="/script",
    tags=["script"],
)

@router.patch("/activate/{pwd}")
async def activate(pwd: str, db: Session = Depends(get_db)):
    """ Auth Search Rights """
    if pwd != settings.admin_pwd:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied",
        )
    result = db.query(admin.Admin).filter(admin.Admin.search_active == False).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Auth search permission already found",
        )

    result.search_active = True
    db.commit()

    return {"message": "Auth search permission has been granted"}

@router.patch("/deactivate/{pwd}")
async def activate(pwd: str, db: Session = Depends(get_db)):
    """ Auth Search Rights """
    if pwd != settings.admin_pwd:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied",
        )
    result = db.query(admin.Admin).filter(admin.Admin.search_active == True).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Auth search permission already restricted",
        )

    result.search_active = False
    db.commit()

    return {"message": "Auth search permission has been restricted"}

@router.get("/check/{pwd}")
async def check(pwd: str, code: str, section: str, campus: str, subject: str, db: Session = Depends(get_db)):
    """ Auth Search Rights """
    if pwd != settings.admin_pwd:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied",
        )
    
    url = f'https://courses.students.ubc.ca/cs/courseschedule?tname=subj-section&course={code}&section={section}&campuscd={campus}&dept={subject}&pname=subjarea'
    headers={'User-Agent':'Mozilla/5.0 (Macintosh; PPC Mac OS X 10_8_2) AppleWebKit/531.2 (KHTML, like Gecko) Chrome/26.0.869.0 Safari/531.2'}
    
    try:
        request_server = requests.get(url, headers=headers)
        logging.info(request_server.text)
        webpage = BeautifulSoup(request_server.text, features="lxml")
        logging.info(webpage.find('table',class_ = "'table").findAll('strong')[1].text)
    except:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No such course exists",
        )

    return {"message": "Checking Completed"}