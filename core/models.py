from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, ForeignKey, Float
from sqlalchemy.orm import relationship
from core.config import Base

class User(Base):
    __tablename__ = "user"
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String)
    password: str = Column(String)

    goals = relationship("Goal", back_populates="user")

class Excercise(Base):
    __tablename__ = "excercise"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)
    description: str = Column(String)
    instructions: str = Column(String)

    excercise_muscles = relationship("ExcerciseMuscle", back_populates="excercise")
    excercise_workout = relationship("ExcerciseWorkout", back_populates="excercise")
    goals = relationship("Goal", back_populates="excercise")
    
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
    user_id: int = Column(Integer, ForeignKey("user.id"))
    name: str = Column(String)
    frequency: int = Column(Integer)
    duration: float = Column(Float)
    goals: str = Column(String)

    excercises = relationship("ExcerciseWorkout", back_populates="workout")

class ExcerciseWorkout(Base):
    __tablename__ = "excercise_workout"
    id: int = Column(Integer, primary_key=True, index=True)
    excercise_id: int = Column(Integer, ForeignKey("excercise.id"))
    workout_id: int = Column(Integer, ForeignKey("workout_plan.id"))
    repetitions: int = Column(Integer)
    sets: int = Column(Integer)

    excercise = relationship("Excercise", back_populates="excercise_workout")
    workout = relationship("WorkoutPlan", back_populates="excercises")

class Goal(Base):
    __tablename__ = "goal"
    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("user.id"))
    excercise_id: int = Column(Integer, ForeignKey("excercise.id"))
    achieved: Boolean = Column(Boolean)
    weight: float = Column(Integer)
    sets: int = Column(Integer)
    repetitions: int = Column(Integer)

    user = relationship("User", back_populates="goals")
    excercise = relationship("Excercise", back_populates="goals")