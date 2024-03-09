from pydantic import BaseModel, Field
from typing import List

class UserSchema(BaseModel):
    username: str = Field(default=None)
    password: str = Field(default=None)

class ExcerciseWorkoutSchema(BaseModel):
    id: int = Field(default=None)
    repetitions: int = Field(default=None)
    sets: int = Field(default=None)

class WorkoutPlanSchema(BaseModel):
    name: str = Field(default=None)
    frequency: int = Field(default=None)
    duration: float = Field(default=None)
    goals: str = Field(default=None)
    excercises: List[ExcerciseWorkoutSchema] = Field(default=None)

class GoalSchema(BaseModel):
    name: str = Field(default=None)
    excercise_id: int = Field(default=None)
    weight: float = Field(default=None)
    sets: int = Field(default=None)
    repetitions: int = Field(default=None)
    repetitions: int = Field(default=None)
    achieved: bool = Field(default=False)
    date: str = Field(default=None)

class WeightTrackerSchema(BaseModel):
    weight: float = Field(default=None)
    date: str = Field(default=None, example="2022-01-01")