from datetime import datetime
from typing import Optional

from sqlalchemy import UUID, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from app.connectors.native.stores.base import BaseObject
from app.connectors.native.utils import sql_value_to_typed_value

Base = declarative_base()


class UserORM(Base):
    __tablename__ = "user"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    usage = Column(Integer, nullable=False)
    api_key = Column(UUID, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=func.now()
    )  # Automatically use the current timestamp of the database server upon creation
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )  # Automatically use the current timestamp of the database server upon creation and update


class User(BaseObject):
    id: Optional[str] = None
    name: str
    email: str
    usage: int = 0
    api_key: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def local(
        cls,
        id: str,
        name: str,
        email: str,
        usage: int,
    ):
        return User(
            id=id,
            name=name,
            email=email,
            usage=usage,
            api_key=cls.generate_id(id=id, name=name, email=email),
        )

    @classmethod
    def remote(
        cls,
        **kwargs,
    ):
        return cls(
            id=sql_value_to_typed_value(dict=kwargs, key="id", type=str),
            name=sql_value_to_typed_value(dict=kwargs, key="name", type=str),
            email=sql_value_to_typed_value(dict=kwargs, key="email", type=str),
            usage=sql_value_to_typed_value(dict=kwargs, key="usage", type=int),
            api_key=sql_value_to_typed_value(dict=kwargs, key="api_key", type=str),
            created_at=sql_value_to_typed_value(
                dict=kwargs, key="created_at", type=datetime
            ),
            updated_at=sql_value_to_typed_value(
                dict=kwargs, key="updated_at", type=datetime
            ),
        )
