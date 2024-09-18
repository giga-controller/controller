import logging
import os
from typing import Any, Optional, Type

from asyncpg.pgproto.pgproto import UUID as AsyncpgUUID
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel
from sqlalchemy import (
    UUID,
    BinaryExpression,
    and_,
    column,
    delete,
    or_,
    select,
    true,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.sql import text

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

load_dotenv(find_dotenv(filename=".env"))
DATABASE_URL = os.environ.get("DATABASE_URL")


class Orm:
    def __init__(self):
        self.engine = create_async_engine(
            url=DATABASE_URL,
            echo=False,
        )
        self.sessionmaker = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get(
        self,
        orm_model: Type[DeclarativeMeta],
        pydantic_model: Type[BaseModel],
        filters: dict[str, Any],
        batch_size: int = 6500,
    ) -> list:
        """Fetches entries from the specified table based on the filters provided.

        Args:
            orm_model (Type[DeclarativeMeta]): The SQLAlchemy ORM model to fetch data of.
            pydantic_model (Type[BaseModel]): The pydantic model to validate the ORM model to.
            filters (list[dict): The filters to apply to the query.

        Returns:
            list: A list of objects that match the filters.
        """
        results = []
        offset = 0
        async with self.sessionmaker() as session:
            while True:
                query = select(orm_model)
                filter_expression, params = _build_filter(orm_model, filters)
                query = query.filter(filter_expression)
                query = query.limit(batch_size).offset(offset)
                batch_results = await session.execute(query, params)
                batch_results = batch_results.scalars().all()
                if not batch_results:
                    break

                results.extend(batch_results)
                offset += batch_size
                log.info(f"Fetching {results} from database")

        if not results:
            return []

        stringified_results = []
        for result in results:
            result_dict = result.__dict__
            for key, value in result_dict.items():
                if isinstance(value, (UUID, AsyncpgUUID)):
                    result_dict[key] = str(value)
            stringified_results.append(result_dict)

        return [pydantic_model.model_validate(result) for result in stringified_results]

    async def post(
        self, orm_model: Type[DeclarativeMeta], data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Inserts entries into the specified table.

        Args:
            orm_model (Type[DeclarativeMeta]): The SQLAlchemy ORM model to insert data into.
            data (list[dict[str, Any]]): The data to insert.

        Returns:
            list[dict[str, Any]]: The data that was inserted
        """
        orm_instances = [orm_model(**item) for item in data]
        async with self.sessionmaker() as session:
            session.add_all(orm_instances)
            await session.flush()
            await session.commit()
            log.info(f"Inserted {len(data)} rows into {orm_model.__tablename__}")
        return data

    async def update(
        self,
        orm_model: Type[DeclarativeMeta],
        filters: dict[str, Any],
        updated_data: Optional[dict[str, Any]],
        increment_field: Optional[str],
    ):
        """Updates entries in the specified table based on the filters provided.

        Args:
            orm_model (Type[DeclarativeMeta]): The SQLAlchemy model to update data of.
            filters (dict): The filters to apply to the query.
            updated_data (dict): The updates to apply to the target rows.
        """
        async with self.sessionmaker() as session:
            filter_expression, params = _build_filter(orm_model, filters)

            update_stmt = update(orm_model).where(filter_expression)

            if increment_field:
                update_stmt = update_stmt.values(
                    {increment_field: column(increment_field) + 1}
                )

            else:
                update_stmt = update_stmt.values(**updated_data)

            await session.execute(update_stmt, params)
            await session.commit()
            log.info(f"Updated rows in {orm_model.__tablename__}")


def _build_filter(
    model: Type[DeclarativeMeta], filter_dict: dict[str, Any], param_prefix: str = "p"
) -> tuple[BinaryExpression, dict]:
    """Recursively builds a SQLAlchemy filter expression from the provided filter dictionary."""
    if not filter_dict:
        return true(), {}

    if "boolean_clause" in filter_dict:
        conditions = []
        params = {}
        for idx, condition in enumerate(filter_dict["conditions"]):
            sub_condition, sub_params = _build_filter(
                model, condition, f"{param_prefix}_{idx}"
            )
            conditions.append(sub_condition)
            params.update(sub_params)

        if len(conditions) == 0:
            return true(), {}
        elif len(conditions) == 1:
            return conditions[0], params
        else:
            return (
                and_(*conditions)
                if filter_dict["boolean_clause"] == "AND"
                else or_(*conditions)
            ), params

    elif (
        "column" in filter_dict and "operator" in filter_dict and "value" in filter_dict
    ):
        column = filter_dict["column"]
        value = filter_dict["value"]
        param_name = f"{param_prefix}"
        param_dict = {param_name: value}

        operators = {
            "=": "{} = :{}",
            "!=": "{} != :{}",
            ">": "{} > :{}",
            "<": "{} < :{}",
            ">=": "{} >= :{}",
            "<=": "{} <= :{}",
            "LIKE": "{} LIKE :{}",
            "IN": "{} IN (:{})" if isinstance(value, (list, tuple)) else "{} IN (:{})",
            "IS NOT": "{} IS NOT NULL" if value is None else "{} != :{}",
        }

        if filter_dict["operator"] in operators:
            if filter_dict["operator"] == "IN" and isinstance(value, (list, tuple)):
                in_params = {f"{param_name}_{i}": v for i, v in enumerate(value)}
                in_clause = ", ".join(f":{param_name}_{i}" for i in range(len(value)))
                return text(f"{column} IN ({in_clause})"), in_params
            else:
                return (
                    text(operators[filter_dict["operator"]].format(column, param_name)),
                    param_dict,
                )
        else:
            raise ValueError(f"Unsupported operator: {filter_dict['operator']}")

    else:
        raise ValueError(f"Invalid filter structure: {filter_dict}")
