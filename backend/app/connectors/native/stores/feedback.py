import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from app.connectors.native.utils import sql_value_to_typed_value

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

Base = declarative_base()


class FeedbackORM(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=True)
    feedback = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )


class Feedback(BaseModel):
    id: Optional[int] = None
    user_id: Optional[str]
    feedback: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def local(cls, user_id: Optional[str], feedback: str):
        return Feedback(
            user_id=user_id,
            feedback=feedback,
        )

    @classmethod
    def remote(
        cls,
        **kwargs,
    ):
        return cls(
            id=sql_value_to_typed_value(dict=kwargs, key="id", type=int),
            user_id=sql_value_to_typed_value(dict=kwargs, key="user_id", type=str),
            feedback=sql_value_to_typed_value(dict=kwargs, key="feedback", type=str),
        )
