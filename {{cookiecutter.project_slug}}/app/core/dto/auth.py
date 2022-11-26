from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserDTO(BaseModel):
    sub: UUID
    email_verified: bool
    preferred_username: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    email: Optional[str] = None
