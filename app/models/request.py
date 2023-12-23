from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.sql.expression import text
from ..utils.db import Base

# TODO: Use enums instead of strings 
class Request(Base):
    __tablename__ = "request"
    request_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    subject = Column(String, nullable=False)
    code = Column(String, nullable=False)
    section = Column(String, nullable=False)
    campus = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    added_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)