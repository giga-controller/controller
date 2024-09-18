import logging
from typing import Any, Optional

from app.connectors.native.stores.user import User, UserORM
from app.connectors.orm import Orm
from app.exceptions.exception import DatabaseError

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

orm = Orm()


class UserService:

    async def login(self, id: str, name: str, email: str) -> User:
        result: list[User] = await orm.get(
            orm_model=UserORM,
            pydantic_model=User,
            filters={
                "boolean_clause": "AND",
                "conditions": [{"column": "id", "operator": "=", "value": id}],
            },
        )
        if len(result) < 1:
            log.info(
                f"User with Clerk ID {id} not found...initiating storage in database"
            )
            created_user: list[dict[str, Any]] = await orm.post(
                orm_model=UserORM,
                data=[
                    User.local(
                        id=id,
                        name=name,
                        email=email,
                        usage=0,
                    ).model_dump()
                ],
            )
            if len(created_user) != 1:
                raise DatabaseError("Error creating user: More than one user returned")
            return User.model_validate(created_user[0])

        return result[0]

    async def get(self, api_key: str) -> User:
        result: list[User] = await orm.get(
            orm_model=UserORM,
            pydantic_model=User,
            filters={
                "boolean_clause": "AND",
                "conditions": [
                    {"column": "api_key", "operator": "=", "value": api_key}
                ],
            },
        )
        if len(result) < 1:
            raise ValueError("Invalid Expand API key")
        elif len(result) > 1:
            raise ValueError("Multiple users found with the same API key")
        return result[0]

    async def increment_usage(self, api_key: str):
        await orm.update(
            orm_model=UserORM,
            filters={
                "boolean_clause": "AND",
                "conditions": [
                    {"column": "api_key", "operator": "=", "value": api_key}
                ],
            },
            updated_data=None,
            increment_field="usage",
        )
