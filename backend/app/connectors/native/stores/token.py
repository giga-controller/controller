from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import UUID, Column, DateTime, Integer, MetaData, String
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy.sql import func

from app.connectors.native.utils import sql_value_to_typed_value

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class TokenORMBase:
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(UUID, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=func.now()
    )  # Automatically use the current timestamp of the database server upon creation
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )  # Automatically use the current timestamp of the database server upon creation and update

    @declared_attr
    def __tablename__(cls):
        return cls.TABLE_NAME


# Dictionary to store created classes
integration_orm_classes = {}


def create_integration_orm(table_name):
    if table_name in integration_orm_classes:
        return integration_orm_classes[table_name]

    class_name = f"IntegrationORM_{table_name}"

    # Check if the table already exists in the metadata
    if table_name in metadata.tables:
        # If it exists, return the existing class
        return integration_orm_classes[table_name]

    # If it doesn't exist, create a new class
    new_class = type(class_name, (TokenORMBase, Base), {"TABLE_NAME": table_name})

    # Store the new class in our dictionary
    integration_orm_classes[table_name] = new_class

    return new_class


class Token(BaseModel):
    id: Optional[int] = None
    api_key: str
    access_token: str
    refresh_token: Optional[str]
    client_id: str
    client_secret: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def local(
        cls,
        api_key: str,
        access_token: str,
        refresh_token: Optional[str],
        client_id: str,
        client_secret: str,
    ):
        return Token(
            api_key=api_key,
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )

    @classmethod
    def remote(
        cls,
        **kwargs,
    ):
        return cls(
            id=sql_value_to_typed_value(dict=kwargs, key="id", type=int),
            api_key=sql_value_to_typed_value(dict=kwargs, key="api_key", type=str),
            access_token=sql_value_to_typed_value(
                dict=kwargs, key="access_token", type=str
            ),
            refresh_token=sql_value_to_typed_value(
                dict=kwargs, key="refresh_token", type=str
            ),
            client_id=sql_value_to_typed_value(dict=kwargs, key="client_id", type=str),
            client_secret=sql_value_to_typed_value(
                dict=kwargs, key="client_secret", type=str
            ),
            created_at=sql_value_to_typed_value(
                dict=kwargs, key="created_at", type=datetime
            ),
            updated_at=sql_value_to_typed_value(
                dict=kwargs, key="updated_at", type=datetime
            ),
        )
