from pydantic import BaseModel, Field
from typing import List

class UserSchema(BaseModel):
    username: str = Field(default=None)
    password: str = Field(default=None)

class ExerciseWorkoutSchema(BaseModel):
    id: int = Field(default=None)
    repetitions: int = Field(default=None)
    sets: int = Field(default=None)
    order: int = Field(default=None)
    break_between_sets: int = Field(default=None)
    break_after_exercise: int = Field(default=None)

class WorkoutPlanSchema(BaseModel):
    name: str = Field(default=None)
    weekdays: str = Field(default=None, example="example: 1010000 means the workout is only on monday and wednesday")
    duration: float = Field(default=None)
    goals: str = Field(default=None)
    exercises: List[ExerciseWorkoutSchema] = Field(default=None)

class GoalSchema(BaseModel):
    name: str = Field(default=None)
    exercise_id: int = Field(default=None)
    weight: float = Field(default=None)
    sets: int = Field(default=None)
    repetitions: int = Field(default=None)
    achieved: bool = Field(default=False)
    date: str = Field(default=None)

class WeightTrackerSchema(BaseModel):
    weight: float = Field(default=None)
    date: str = Field(default=None, example="2022-01-01")

class GetExerciseSchema(BaseModel):
    name: str = Field(default="")
    muscles: List[str] = Field(default=[])