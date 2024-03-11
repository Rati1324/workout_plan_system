from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from core.config import Base
from typing import Optional

class User(Base):
    __tablename__ = "user"
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String)
    password: str = Column(String)

    goals = relationship("Goal", back_populates="user")
    weights = relationship("WeightTracker", back_populates="user")

class Exercise(Base):
    __tablename__ = "exercise"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)
    description: str = Column(String)
    instructions: str = Column(String)

    exercise_muscles = relationship("ExerciseMuscle", back_populates="exercise")
    exercise_workout = relationship("ExerciseWorkout", back_populates="exercise")
    goals = relationship("Goal", back_populates="exercise")
    
class ExerciseMuscle(Base):
    __tablename__ = "exercise_muscle"
    id: int = Column(Integer, primary_key=True, index=True)
    exercise_id: int = Column(Integer, ForeignKey("exercise.id"))
    muscle_id: int = Column(Integer, ForeignKey("muscle.id"))

    exercise = relationship("Exercise", back_populates="exercise_muscles")
    muscle = relationship("Muscle", back_populates="exercise_muscles")

class Muscle(Base):
    __tablename__ = "muscle"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)

    exercise_muscles = relationship("ExerciseMuscle", back_populates="muscle")

class WorkoutPlan(Base):
    __tablename__ = "workout_plan"
    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("user.id"))
    name: str = Column(String)
    frequency: int = Column(Integer)
    duration: float = Column(Float)
    goals: str = Column(String)

    exercises = relationship("ExerciseWorkout", back_populates="workout")

class ExerciseWorkout(Base):
    __tablename__ = "exercise_workout"
    id: int = Column(Integer, primary_key=True, index=True)
    exercise_id: int = Column(Integer, ForeignKey("exercise.id"))
    workout_id: int = Column(Integer, ForeignKey("workout_plan.id"))
    repetitions: int = Column(Integer)
    sets: int = Column(Integer)
    order: int = Column(Integer)
    break_time: float = Column(Integer)

    exercise = relationship("Exercise", back_populates="exercise_workout")
    workout = relationship("WorkoutPlan", back_populates="exercises")

class Goal(Base):
    __tablename__ = "goal"
    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("user.id"))
    exercise_id: int = Column(Integer, ForeignKey("exercise.id"))
    achieved: Boolean = Column(Boolean)
    weight: Optional[float] = Column(Integer)
    sets: int = Column(Integer)
    repetitions: int = Column(Integer)
    date: Date = Column(Date)
    user = relationship("User", back_populates="goals")
    exercise = relationship("Exercise", back_populates="goals")

class WeightTracker(Base):
    __tablename__ = "weight_tracker"
    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float)
    date: Optional[str] = Column(Date, default=None)
    user_id: int = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", back_populates="weights")