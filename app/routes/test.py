from fastapi import APIRouter, Depends, HTTPException, Response, status
# from sqlalchemy.orm import Session
# from ...schemas.v1 import report_schemas_v1 as report_schemas
# from ...utils.database import get_db
# from ...models.v1 import (
#     report_models_v1 as report_models,
#     listing_models_v1 as listing_models,
#     user_models_v1 as user_models,
# )
# from app.firebase_auth import get_current_user

router = APIRouter(
    prefix="/report",
    tags=["report"],
)


@router.post(
    "/"
)
def report_listing(
):
    """Post reports for a listing"""

   