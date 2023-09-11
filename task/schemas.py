from pydantic import BaseModel, validator


class UserCRUD(BaseModel):
    name: str


class CustomValidationError(BaseModel):
    detail: str
