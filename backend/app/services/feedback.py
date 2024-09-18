from typing import Optional

from app.connectors.native.stores.feedback import Feedback, FeedbackORM
from app.connectors.orm import Orm

orm = Orm()


class FeedbackService:
    async def post(self, id: Optional[str], feedback: str):
        await orm.post(
            orm_model=FeedbackORM,
            data=[Feedback.local(user_id=id, feedback=feedback).model_dump()],
        )
