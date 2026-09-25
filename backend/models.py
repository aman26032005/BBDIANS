from sqlalchemy import Column, Integer, Text, DateTime, Boolean
from datetime import datetime

from .database import Base


class Confession(Base):
    __tablename__ = "confessions"

    id = Column(Integer, primary_key=True, index=True)

    message = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    is_read = Column(
        Boolean,
        default=False
    )