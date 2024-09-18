import logging
from typing import Optional

from app.connectors.native.stores.token import (
    Token,
    TokenORMBase,
    create_integration_orm,
)
from app.connectors.orm import Orm
from app.exceptions.exception import DatabaseError

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

orm = Orm()


class TokenService:

    async def post(
        self,
        api_key: str,
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
        table_name: str,
    ):
        TokenORM = create_integration_orm(table_name=table_name)

        await orm.post(
            orm_model=TokenORM,
            data=[
                Token.local(
                    api_key=api_key,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    client_id=client_id,
                    client_secret=client_secret,
                ).model_dump()
            ],
        )

    async def get(self, api_key: str, table_name: str) -> Optional[Token]:
        TokenORM = create_integration_orm(table_name=table_name)

        result: list[Token] = await orm.get(
            orm_model=TokenORM,
            pydantic_model=Token,
            filters={
                "boolean_clause": "AND",
                "conditions": [
                    {"column": "api_key", "operator": "=", "value": api_key}
                ],
            },
        )
        if len(result) > 1:
            raise DatabaseError(
                f"User with api key {api_key} has more than one set of tokens in the {table_name} table"
            )
        elif len(result) == 0:
            log.info(
                f"User with api key {api_key} not found in the {table_name} token table"
            )
            return None

        return result[0]

    async def update(
        self,
        id: str,
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
        table_name: str,
    ):
        TokenORM = create_integration_orm(table_name=table_name)
        await orm.update(
            orm_model=TokenORM,
            filters={
                "boolean_clause": "AND",
                "conditions": [{"column": "id", "operator": "=", "value": id}],
            },
            updated_data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            increment_field=None,
        )
