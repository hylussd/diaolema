"""通用响应结构。"""
from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    data: dict | list | None = None
    msg: str = ""
