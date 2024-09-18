import hashlib
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import ARRAY, JSON, UUID, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from app.connectors.native.utils import sql_value_to_typed_value

Base = declarative_base()


class MessageORM(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(UUID, nullable=False)
    integrations = Column(ARRAY(String), nullable=False)
    chat_history = Column(ARRAY(JSON), nullable=False)
    instance = Column(UUID, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=func.now()
    )  # Automatically use the current timestamp of the database server upon creation
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )  # Automatically use the current timestamp of the database server upon creation and update


class Message(BaseModel):
    id: Optional[int] = None
    api_key: str
    integrations: list[str]
    chat_history: list[dict]
    instance: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def local(
        cls,
        chat_history: list[dict],
        api_key: str,
        integrations: list[str],
        instance: Optional[str],
    ):
        if not instance:
            data = f"{chat_history}{api_key}{integrations}{datetime.now().isoformat()}"
            instance = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS, hashlib.sha256(data.encode()).hexdigest()
                )
            )
        return Message(
            api_key=api_key,
            integrations=integrations,
            chat_history=chat_history,
            instance=instance,
        )

    @classmethod
    def remote(
        cls,
        **kwargs,
    ):
        return cls(
            id=sql_value_to_typed_value(dict=kwargs, key="id", type=int),
            api_key=sql_value_to_typed_value(dict=kwargs, key="api_key", type=str),
            integrations=sql_value_to_typed_value(
                dict=kwargs, key="integrations", type=list
            ),
            chat_history=sql_value_to_typed_value(
                dict=kwargs, key="chat_history", type=list
            ),
            instance=sql_value_to_typed_value(dict=kwargs, key="instance", type=str),
            created_at=sql_value_to_typed_value(
                dict=kwargs, key="created_at", type=datetime
            ),
            updated_at=sql_value_to_typed_value(
                dict=kwargs, key="updated_at", type=datetime
            ),
        )
