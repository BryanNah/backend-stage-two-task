from pydantic import BaseModel, validator


class UserCRUD(BaseModel):
    name: str


# Pydantic model for returning a user (includes 'id')
class UserReturn(UserCRUD):
    id: int

    class Config:
        orm_mode = True


class CustomValidationError(BaseModel):
    detail: str
