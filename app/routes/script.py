from fastapi import APIRouter, Depends, HTTPException, Response, status
from ..models import admin
from sqlalchemy.orm import Session
from ..utils.db import get_db
from ..config import settings


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
    