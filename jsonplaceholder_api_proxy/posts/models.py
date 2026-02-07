from typing import Annotated

from pydantic import BaseModel, Field


class _PostBase(BaseModel):
    title: str
    body: str


class PostCreate(_PostBase):
    user_id: Annotated[int, Field(alias="userId", gt=0)]


class PostRead(PostCreate):
    id: Annotated[int, Field(gt=0)]


class PostUpdate(_PostBase):
    pass
