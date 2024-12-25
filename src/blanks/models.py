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
    # series: Optional[str] = None
    # number: Optional[int] = None
    comment: Optional[str] = None
    status: Optional[BlankState | int] = None
    

class BlankRangeInDTO(BaseModel):
    """
    WARN:
    range include both borders 
    """
    series: str
    start: int
    end: int

    def get_range(self):
        return range(self.start, self.end+1)
