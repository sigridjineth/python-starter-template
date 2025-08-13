from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime = datetime.now()

    def greeting(self) -> str:
        return f"Hello, {self.name}!"

