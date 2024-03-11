import json, time, asyncio
from fastapi import FastAPI, Depends, HTTPException, WebSocket, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from core.utils import get_db, get_hashed_password, create_jwt_token, get_current_user, oauth2_scheme
from core.models import User, Exercise, WorkoutPlan, ExerciseWorkout, Goal, WeightTracker
from core.config import SessionLocal
from core.schemas import UserSchema, WorkoutPlanSchema, GoalSchema, WeightTrackerSchema
import re
from seed_db import seed, clear
from datetime import datetime
from starlette.templating import Jinja2Templates
import redis
from urllib.parse import parse_qs

templates = Jinja2Templates(directory="templates")

app = FastAPI()
# Base.metadata.create_all(bind=engine)

# seed()
# clear()

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

@app.post("/get_exercises")
async def get_exercises(dependencies = Depends(get_current_user), db: Session = Depends(get_db)):
    exercises = db.query(exercise).all()

    result = []
    for exercise in exercises:
        muscles = []
        for muscle in exercise.exercise_muscles:
            muscles.append(muscle.muscle.name)
        result.append({"id": exercise.id, "exercise": exercise.name, "muscles": muscles})
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

    for exercise in workout_plan.exercises:
        print(exercise.repetitions)
        db_exercise_workout = exerciseWorkout(
            exercise_id = exercise.id,
            workout_id = plan_id,
            repetitions = exercise.repetitions,
            sets = exercise.sets,
        )
        db_workout_plan.exercises.append(db_exercise_workout)
        db.add(db_exercise_workout)
    db.commit()
    return {"response": "created successfully"}

@app.post("/create_goal")
async def create_goal(dependencies = Depends(get_current_user), db: Session = Depends(get_db), goal: GoalSchema = None):
    if goal.date is None:
        goal.date = datetime.now()
    db_goal = Goal(
        user_id = dependencies.id,
        exercise_id = goal.exercise_id,
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

@app.get("/temp")
async def get():
    return {"result": "result"}

@app.get("/get_workout_plans")
async def get_workout_plans(dependencies = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = dependencies.id
    workout_plans = db.query(WorkoutPlan).filter_by(user_id=user_id).all()
    result = []
    for plan in workout_plans:
        exercises = []
        for exercise in plan.exercises:
            exercise_name = db.query(exercise).filter_by(id=exercise.exercise_id).first().name
            exercises.append({"id": exercise.exercise_id, "name": exercise_name, "repetitions": exercise.repetitions, "sets": exercise.sets})
        result.append({"id": plan.id, "name": plan.name, "frequency": plan.frequency, "duration": plan.duration, "goals": plan.goals, "exercises": exercises})
    return workout_plans

r = redis.Redis(host='redis_service', port=6379, decode_responses=True)

@app.websocket("/workout_session")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await websocket.accept()
    try:
        user = get_current_user(db=SessionLocal(), token=token)
    except HTTPException:
        await websocket.send_text("Invalid token")
        await websocket.close()
        return None

    # await websocket.send_text(user)

    # while 1:
    #     data = await websocket.receive_text()
        # json_data = json.loads(data)

        # if json_data["action"] == "store":
        #     r.set("value", json_data["value"])
        # elif json_data["action"] == "retrieve":
        #     value = r.get(json_data["key"])
        #     await websocket.send_text(f"value from redis: {value}")
