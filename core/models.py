from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, ForeignKey, Float
from sqlalchemy.orm import relationship
from core.config import Base

class User(Base):
    __tablename__ = "user"
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String)
    password: str = Column(String)

class Excercise(Base):
    __tablename__ = "excercise"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)
    description: str = Column(String)
    instructions: str = Column(String)
    excercise_muscles = relationship("ExcerciseMuscle", back_populates="excercise")

class ExcerciseMuscle(Base):
    __tablename__ = "excercise_muscle"
    id: int = Column(Integer, primary_key=True, index=True)
    excercise_id: int = Column(Integer, ForeignKey("excercise.id"))
    muscle_id: int = Column(Integer, ForeignKey("muscle.id"))
    excercise = relationship("Excercise", back_populates="excercise_muscles")
    muscle = relationship("Muscle", back_populates="excercise_muscles")

class Muscle(Base):
    __tablename__ = "muscle"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)
    excercise_muscles = relationship("ExcerciseMuscle", back_populates="muscle")

class WorkoutPlan(Base):
    __tablename__ = "workout_plan"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)
    frequency: int = Column(Integer)
    duration: float = Column(Float)
    goals: str = Column(String)
    user_id: int = Column(Integer, ForeignKey("user.id"))

class ExcerciseWorkout(Base):
    __tablename__ = "excercise_workout"
    id: int = Column(Integer, primary_key=True, index=True)
    excercise_id: int = Column(Integer, ForeignKey("excercise.id"))
    workout_id: int = Column(Integer, ForeignKey("workout_plan.id"))
    repetitions: int = Column(Integer)
    sets: int = Column(Integer)
    # excercise: Excercise = relationship("Excercise", back_populates="workouts")
    # workout = relationship("Workout", back_populates="excercises")
    excercise = relationship("Excercise", backref="excercises")
    workout = relationship("WorkoutPlan", backref="workout_plans")

