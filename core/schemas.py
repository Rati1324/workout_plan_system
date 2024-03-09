from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    username: str = Field(default=None)
    password: str = Field(default=None)

class WorkoutPlanSchema(BaseModel):
    name: str = Field(default=None)
    frequency: int = Field(default=None)
    duration: float = Field(default=None)
    goals: str = Field(default=None)