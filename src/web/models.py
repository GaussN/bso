from enum import Enum
import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field
from pydantic import field_validator, ValidationError  # noqa


class BlankState(Enum):
    Clean = 0
    Use = 1
    Spoiled = 2
    Lost = 3


class BlankInDTO(BaseModel):
    date: Optional[dt.date] = None
    series: str = Field(max_length=2, min_length=2)
    number: int 
    comment: Optional[str] = ""
    status: Optional[BlankState | int] = 0

    def __eq__(self, other) -> bool:
        return self.series == other.series and self.number == other.number

    def full_compare(self, other) -> bool:
        for o1, o2 in zip(self.__dict__.values(), other.__dict__.values()):
            if o1 != o2:
                return False
        return True


class BlankOutDTO(BlankInDTO):
    id: Optional[int] = -1
    created_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None
    deleted_at: Optional[dt.datetime] = None


class BlankUpdateDTO(BlankInDTO):
    id: int
    series: Optional[str] = None
    number: Optional[int] = None
    comment: Optional[str] = None
    status: Optional[BlankState | int] = None
    
    def get_update_stmt(self) -> tuple[str, tuple]:
        if isinstance(self.status, BlankState):
            self.status = self.status.value  # WARNING: cs
        params = []
        def _(k, v):
            params.append(v)
            return f"{k}=?"
        sets = ",".join((_(k, v) for k,v in self.__dict__.items() if v and k != "id"))
        return f"UPDATE blanks SET {sets},updated_at=datetime('now') WHERE id=?", (*params, self.id)    
