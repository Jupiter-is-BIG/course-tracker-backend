from fastapi import APIRouter, Depends, HTTPException, Response, status
from ..models import request
from sqlalchemy.orm import Session
from ..utils.db import get_db
from ..config import settings

router = APIRouter(
    prefix="/request",
    tags=["request"],
)

@router.post("/", status_code=201)
async def push_request(subject: str, code: str, section: str, campus: str, pwd: str, db: Session = Depends(get_db)):
    """ Pushes new tracking requests """

    if pwd != settings.admin_pwd:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied",
        )
    
    if not (subject and code and section and campus):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Wrong format",
        )
         
    new_request = request.Request(
        subject=subject,
        code=code,
        section=section,
        campus=campus
    )

    db.add(new_request)
    db.commit()

    return {"message": f"Resquest for {subject} {code} {section} on {campus} campus has been registered successfully"}

