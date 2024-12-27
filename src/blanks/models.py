import re
import datetime
from enum import Enum
from typing import Optional, Annotated, Any

from pydantic import BaseModel
from pydantic import AfterValidator

SERIES_PATTERN = r"[A-ZА-Я]{2}"
MAX_NUMBER = 9999999


class SeriesValidator:
    def __init__(self, pattern: str):
        self._patter = re.compile(pattern)

    def __call__(self, series: str) -> str:
        if self._patter.fullmatch(series):
            return series
        raise ValueError(f"seies should have full match {self._patter} ")


class NumberValidator:
    def __init__(self, max_value: int):
        self._max_value = max_value

    def __call__(self, number: int) -> int:
        if number <= self._max_value:
            return number
        raise ValueError(f"number should be in range (0, {self._max_value}] ")


class BlankStatus(Enum):
    Clean = 0
    Use = 1
    Spoiled = 2
    Lost = 3


class BlankInDTO(BaseModel):
    date: Optional[datetime.date] = None
    series: Annotated[
        str, 
        AfterValidator(SeriesValidator(pattern=SERIES_PATTERN))
    ]
    number: Annotated[
        int, 
        AfterValidator(NumberValidator(max_value=MAX_NUMBER))
    ]
    comment: Optional[str] = ""
    status: Optional[BlankStatus | int] = 0

    def __eq__(self, other) -> bool:
        return self.series == other.series and self.number == other.number

    def full_compare(self, other) -> bool:
        for o1, o2 in zip(self.__dict__.values(), other.__dict__.values()):
            if o1 != o2:
                return False
        return True


class BlankOutDTO(BlankInDTO):
    id: Optional[int] = -1
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    deleted_at: Optional[datetime.datetime] = None


class Undefined(object):
    pass


class BlankUpdateDTO(BaseModel):
    id: int
    date: datetime.date | None = Undefined()
    comment: str | None = Undefined()
    status: BlankStatus | int | None = Undefined()
    

class BlankRangeInDTO(BaseModel):
    """
    WARN:
    range include both borders 
    """
    series: Annotated[
        str, 
        AfterValidator(SeriesValidator(pattern=SERIES_PATTERN))
        ]
    start: Annotated[
        int, 
        AfterValidator(NumberValidator(max_value=MAX_NUMBER))
    ]
    end: Annotated[
        int, 
        AfterValidator(NumberValidator(max_value=MAX_NUMBER))
    ]

    def model_post_init(self, context: Any):
        if self.start > self.end:
            self.start, self.end = self.end, self.start

    def get_range(self):
        return range(self.start, self.end+1)
