from sqlalchemy import Column, Integer, TIMESTAMP, Boolean
from sqlalchemy.sql.expression import text
from ..utils.db import Base


class Admin(Base):
    __tablename__ = "admin"
    search_active = Column(Boolean, primary_key=True, nullable=False, default=False)
    frequency = Column(Integer, nullable=False, default=300)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)