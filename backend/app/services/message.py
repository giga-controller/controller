import logging
from typing import Optional

from app.connectors.native.stores.message import Message, MessageORM
from app.connectors.orm import Orm
from app.exceptions.exception import DatabaseError
from app.models.integrations.base import Integration

orm = Orm()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MessageService:
    async def post(
        self,
        chat_history: list[Message],
        api_key: str,
        integrations: list[Integration],
        instance: Optional[str],
    ) -> str:
        # This method logs the user chat history and returns the instance uuid
        data = Message.local(
            chat_history=[msg.model_dump() for msg in chat_history],
            api_key=api_key,
            integrations=integrations,
            instance=instance,
        ).model_dump()
        if not instance:
            log.info("No message entry for this instance. Creating new entry.")
            entry: list[Message] = await orm.post(
                orm_model=MessageORM,
                data=[data],
            )
            log.info(f"Message entry posted: {entry}")
            if len(entry) != 1:
                raise DatabaseError(
                    "Error creating message: More/Fewer than one message returned"
                )
            instance = Message.model_validate(entry[0]).instance
            return instance

        log.info("Update message entry for this instance.")
        await orm.update(
            orm_model=MessageORM,
            filters={
                "boolean_clause": "AND",
                "conditions": [
                    {"column": "instance", "operator": "=", "value": instance}
                ],
            },
            updated_data={
                "chat_history": data["chat_history"],
                "integrations": data["integrations"],
            },
            increment_field=None,
        )
        return instance
