import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.utils import get_db, get_hashed_password, create_jwt_token, get_current_user
from core.models import User, Excercise, WorkoutPlan, ExcerciseWorkout, Goal, WeightTracker
from core.config import Base, engine
from core.schemas import UserSchema, WorkoutPlanSchema, GoalSchema, WeightTrackerSchema
import re
from seed_db import seed, clear
from datetime import datetime

app = FastAPI()
Base.metadata.create_all(bind=engine)

# seed()
# clear()
@app.get("/")
async def main(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.post("/register")
async def register(user_data: UserSchema, db: Session = Depends(get_db)):
    password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"

    if not re.match(password_regex, user_data.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter, one uppercase letter, one digit, and be at least 8 characters long")

    if len(user_data.username) < 6:
        raise HTTPException(status_code=400, detail="Username must be over 6 characters long")
 
    hashed_password = get_hashed_password(user_data.password)

    db_user = User(
        username = user_data.username,
        password = hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    token = create_jwt_token(user_data.username)
    return {"response": token}

@app.post("/login")
async def login(db: Session = Depends(get_db), user_data: OAuth2PasswordRequestForm = Depends()):
    print(user_data)
    user = db.query(User).filter_by(username=user_data.username).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")

    hashed_password = get_hashed_password(user_data.password)

    if not hashed_password != user.password:
        raise HTTPException(status_code=400, detail="Invalid password")
    token = create_jwt_token(user_data.username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/get_excercises")
async def get_excercises(dependencies = Depends(get_current_user), db: Session = Depends(get_db)):
    excercises = db.query(Excercise).all()

    result = []
    for excercise in excercises:
        muscles = []
        for muscle in excercise.excercise_muscles:
            muscles.append(muscle.muscle.name)
        result.append({"id": excercise.id, "excercise": excercise.name, "muscles": muscles})
    return result

@app.post("/create_plan")
async def create_plan(dependencies = Depends(get_current_user), db: Session = Depends(get_db), workout_plan: WorkoutPlanSchema = None):
    db_workout_plan = WorkoutPlan(
        user_id = dependencies.id,
        name = workout_plan.name,
        frequency = workout_plan.frequency,
        duration = workout_plan.duration,
        goals = workout_plan.goals,
    )
    db.add(db_workout_plan)
    db.commit()

    plan_id = db_workout_plan.id

    for excercise in workout_plan.excercises:
        print(excercise.repetitions)
        db_excercise_workout = ExcerciseWorkout(
            excercise_id = excercise.id,
            workout_id = plan_id,
            repetitions = excercise.repetitions,
            sets = excercise.sets,
        )
        db_workout_plan.excercises.append(db_excercise_workout)
        db.add(db_excercise_workout)
    db.commit()
    return {"response": "created successfully"}

@app.post("/create_goal")
async def create_goal(dependencies = Depends(get_current_user), db: Session = Depends(get_db), goal: GoalSchema = None):
    if goal.date is None:
        goal.date = datetime.now()
    db_goal = Goal(
        user_id = dependencies.id,
        excercise_id = goal.excercise_id,
        weight = goal.weight,
        sets = goal.sets,
        repetitions = goal.repetitions,
        achieved = goal.achieved,
        date = goal.date,
    )
    db.add(db_goal)
    db.commit()
    return {"response": "Goal created successfully"}
 
@app.post("/track_weight")
async def track_weight(dependencies = Depends(get_current_user), db: Session = Depends(get_db), weight_info: WeightTrackerSchema = None):
    if weight_info.date is None:
        weight_info.date = datetime.now()

    db_weight = WeightTracker(
        user_id = dependencies.id,
        weight = weight_info.weight,
        date = weight_info.date,
    )

    db.add(db_weight)
    db.commit()
    return {"response": "Weight tracked successfully"}