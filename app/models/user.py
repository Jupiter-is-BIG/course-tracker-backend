from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from ..utils.db import Base
from .request import Request

class User(Base):
    __tablename__ = "user"
    user_id = Column(String, primary_key=True, nullable=False)
    user_name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)

class UserRequests(Base):
    __tablename__ = "user_requests"
    user_id = Column(String, ForeignKey('user.user_id'), primary_key=True, nullable=False)
    request_id = Column(Integer, ForeignKey('request.request_id'), primary_key=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)

    user = relationship("User", back_populates="user_requests")
    request = relationship("Request", back_populates="user_requests")

User.user_requests = relationship("UserRequests", back_populates="user")
Request.user_requests = relationship("UserRequests", back_populates="request")