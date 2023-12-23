from fastapi import APIRouter, Depends, HTTPException, Response, status
from ..models import request, user
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..utils.db import get_db
from ..config import settings

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
    current_user = db.query(user.User).filter(user.User.user_name == user_name).first()
    if (not current_user) or current_user.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
        )
    
    if not (subject and code and section and campus):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Wrong format",
        )
    
    if (len(subject) != 4 or len(code) != 3 or len(section) != 3):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Wrong format",
        )
    
    dive = db.query(request.Request).filter(and_(request.Request.subject == subject,request.Request.code == code,request.Request.section == section,request.Request.campus == campus)).first()
    if dive:
        previous_record = db.query(user.UserRequests).filter(and_(user.UserRequests.user_id == current_user.user_id,user.UserRequests.request_id == dive.request_id)).first()
        
        if previous_record:
            previous_record.is_active = True
        else:
            new_record = user.UserRequests(
                user_id = current_user.user_id,
                request_id = dive.request_id,
                is_active = True
            )
            db.add(new_record)
        
        
        dive.is_active = True
        db.commit()
        
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

    return {"message": f"Resquest for {subject} {code} {section} on {campus} campus has been registered successfully"}

