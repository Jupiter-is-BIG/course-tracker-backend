from pydantic import BaseModel

class Subscription(BaseModel):
    subject: str
    code: str
    section: str
    campus: str
    request_id: str
    user_id: str
    is_active: bool

    class Config:
        orm_mode = True