import uuid

from pydantic import BaseModel


class BaseObject(BaseModel):

    class Config:
        orm_mode = True
        from_attributes = True

    @staticmethod
    def generate_id(
        **kwargs,
    ) -> str:
        for k, v in kwargs.items():
            if v is None:
                raise Exception(f"Cannot generate id with None value for key {k}")

        return str(
            uuid.uuid3(uuid.NAMESPACE_DNS, "-".join([str(v) for v in kwargs.values()]))
        )
