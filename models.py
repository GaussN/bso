from typing import Optional, Annotated
from datetime import date

from pydantic import BaseModel, Field
from pydantic import field_validator, ValidationError


class BlankDTO(BaseModel):
    date: Optional[date] 
    series: str = Field(max_length=2, min_length=2)
    number: int  # add digits count validation
    comment: Optional[str] = ""
    status: Optional[int] = 0


class NumberRange(BaseModel):
        start: int
        end: int


class BlankRangeDTO(BaseModel):
    series: str = Field(max_length=2, min_length=2)
    numbers: NumberRange