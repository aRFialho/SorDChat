from pydantic import BaseModel
from typing import Optional


class ChannelBase(BaseModel):
    name: str
    is_private: bool = False
    workspace_id: int


class ChannelCreate(ChannelBase):
    pass


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    is_private: Optional[bool] = None


class ChannelOut(ChannelBase):
    id: int

    class Config:
        from_attributes = True