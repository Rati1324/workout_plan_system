from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    username: str = Field(default=None)
    password: str = Field(default=None)