import re
from .models import User, WorkoutPlan
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .utils import get_db
from datetime import timedelta
from typing import Optional
from .schemas import UserSchema, WorkoutPlanSchema
from .utils import (
    get_hashed_password, create_jwt_token, get_current_user
)

router = APIRouter()

@router.post("/register")
async def register(user_data: UserSchema, db: Session = Depends(get_db)):
    password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"

    check_user = db.query(User).filter_by(username=user_data.username).first()    
    if check_user is not None:
        raise HTTPException(status_code=400, detail="Username already taken")
    
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

@router.post("/login")
async def login(db: Session = Depends(get_db), user_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter_by(username=user_data.username).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")

    hashed_password = get_hashed_password(user_data.password)

    if not hashed_password != user.password:
        raise HTTPException(status_code=400, detail="Invalid password")
    token = create_jwt_token(user_data.username)
    return {"access_token": token, "token_type": "bearer"}

async def get_workout_plans_db(db: Session, user_id: int):
    workout_plans = db.query(WorkoutPlan).filter_by(user_id=user_id).all()
    result = []

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for plan in workout_plans:
        exercises = []

        plan.exercises.sort(key=lambda x: x.order)
        plan_days = plan.weekdays
        days = [weekdays[i] for i in range(len(plan_days)) if plan_days[i] == "1"]
        for exercise in plan.exercises:
            exercise_name = exercise.exercise.name
            break_between_sets = exercise.break_between_sets
            break_after_exercise = exercise.break_after_exercise

            exercises.append({"id": exercise.exercise_id, "name": exercise_name,
                               "repetitions": exercise.repetitions, "sets": exercise.sets,
                               "break_between_sets": break_between_sets, "break_after_exercise": break_after_exercise, "weekdays": days})

        result.append({"id": plan.id, "name": plan.name, "weekdays": plan.weekdays, "duration": plan.duration, "goals": plan.goals, "exercises": exercises})
    return result
