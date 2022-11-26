from typing import Any, Optional

from pydantic import BaseModel, validator

from core.errors import ErrorCategories


class BusinessErrorDTO(BaseModel):
    status: str
    detail: str
    error_type: str = ""
    data: dict = None
    recovery_type: str = ""
    raw_type: str = ""
    category: Optional[ErrorCategories] = None

    @validator("category", pre=True)
    def validate_category(cls, value: Any) -> Any:
        if isinstance(value, str):
            return getattr(ErrorCategories, value, value)
        return value
