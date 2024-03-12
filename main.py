import json, time, asyncio
from fastapi import FastAPI, Depends, HTTPException, WebSocket, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database
from core.utils import get_db, get_hashed_password, create_jwt_token, get_current_user, oauth2_scheme
from core.models import User, Exercise, WorkoutPlan, ExerciseWorkout, Goal, WeightTracker
from core.config import SessionLocal, engine, Base
from core.schemas import UserSchema, WorkoutPlanSchema, GoalSchema, WeightTrackerSchema
import re
from seed_db import seed, clear
from datetime import datetime
import redis
from urllib.parse import parse_qs


app = FastAPI()

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database created.")

# Base.metadata.create_all(bind=engine)
# seed()
# clear()

@app.post("/register")
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

@app.post("/login")
async def login(db: Session = Depends(get_db), user_data: OAuth2PasswordRequestForm = Depends()):
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
    exercises = db.query(Exercise).all()

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

    last_order_num = 0
    for exercise in workout_plan.exercises:
        if exercise.order != last_order_num + 1:
            raise HTTPException(status_code=400, detail="Order of exercises is not correct")
        last_order_num = exercise.order

        db_exercise_workout = ExerciseWorkout(
            exercise_id = exercise.id,
            workout_id = plan_id,
            repetitions = exercise.repetitions,
            sets = exercise.sets,
            break_between_sets = exercise.break_between_sets,
            break_after_exercise = exercise.break_after_exercise,
            order = exercise.order,
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

def get_workout_plans_db(db: Session, user_id: int):
    workout_plans = db.query(WorkoutPlan).filter_by(user_id=user_id).all()
    result = []
    for plan in workout_plans:
        exercises = []
        for exercise in plan.exercises:
            # exercise_name = db.query(Exercise).filter_by(id=exercise.exercise_id).first().name
            exercise_name = exercise.exercise.name
            break_between_sets = exercise.break_between_sets
            break_after_exercise = exercise.break_after_exercise

            exercises.append({"id": exercise.exercise_id, "name": exercise_name,
                               "repetitions": exercise.repetitions, "sets": exercise.sets,
                               "break_between_sets": break_between_sets, "break_after_exercise": break_after_exercise})
        result.append({"id": plan.id, "name": plan.name, "frequency": plan.frequency, "duration": plan.duration, "goals": plan.goals, "exercises": exercises})
    return result

@app.get("/get_workout_plans")
async def get_workout_plans(dependencies = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = dependencies.id
    workout_plans = get_workout_plans_db(db, user_id)
    return workout_plans

r = redis.Redis(host='redis_service', port=6379, decode_responses=True)



# r.flushall()
@app.websocket("/workout_session")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await websocket.accept()
    db = SessionLocal()
    user = None
    try:
        user = get_current_user(db, token=token)
    except HTTPException:
        await websocket.send_text("Invalid token")
        await websocket.close()
        return None

    await websocket.send_text("Connected successfully")
    user_workout_plans = get_workout_plans_db(db, user.id)

    def finish_set():
        cur_set = int(r.get("cur_set"))
        r.set("break", r.get("break_between_sets"))
        r.set("cur_set", cur_set + 1)
        r.set("status", "break_after_set")

    def finish_exercise(exercises):
        cur_exercise_index = int(r.get("cur_exercise_index")) + 1
        r.set("break", r.get("break_after_exercise"))
        r.set("cur_exercise_index", cur_exercise_index)
        r.set("cur_exercise_name", exercises[cur_exercise_index]["name"])
        r.set("cur_set", 1)
        r.set("total_sets", exercises[cur_exercise_index]["sets"])
        r.set("status", "break_after_exercise")

    while 1:
        request = await websocket.receive_text()

        json_request = json.loads(request)
        action = json_request["action"]

        if "plan_id" in json_request:
            cur_plan = [plan for plan in user_workout_plans if plan["id"] == json_request["plan_id"]][0]

        if action == "start_session":
            cur_exercise = cur_plan["exercises"][0]
            total_exercises = len(cur_plan["exercises"])

            r.set("total_exercises", total_exercises)
            r.set("cur_exercise_index", 0)
            r.set("cur_exercise_name", cur_exercise["name"])
            r.set("break_after_exercise", cur_exercise["break_after_exercise"])

            r.set("total_sets", cur_exercise["sets"])
            r.set("cur_set", 1)
            r.set("break_between_sets", cur_exercise["break_between_sets"])

            r.set("status", "started")

            cur_exercise = cur_plan["exercises"][int(r.get("cur_exercise_index"))]
            await websocket.send_text(json.dumps({"status": "session_started", "cur_exercise": cur_exercise}))

        elif action == "finish_set":
            cur_set = r.get("cur_set")
            total_sets = r.get("total_sets")

            cur_exercise_index = int(r.get("cur_exercise_index"))
            total_exercises = int(r.get("total_exercises"))

            if cur_set == total_sets:
                if (cur_exercise_index + 1) == total_exercises:
                    await websocket.send_text(json.dumps({"status": "session_ended"}))
                    await websocket.close(code=1000, reason="session_ended")
                else:
                    finish_exercise(cur_plan["exercises"])
            else:
                finish_set()

            status = r.get("status")
            await websocket.send_text(json.dumps({"status": status}))

            await asyncio.sleep(int(r.get("break")))

            if r.get("status") == "break_after_set":
                await websocket.send_text(json.dumps({"status": "started"}))

            else:
                cur_exercise = cur_plan["exercises"][int(r.get("cur_exercise_index"))]
                cur_set = r.get("cur_set")
                await websocket.send_text(json.dumps({"status": "set_started", "cur_exercise": cur_exercise, "cur_set": cur_set}))


        if r.get("status") == "session_ended":
            break
        # await websocket.send_text(json.dumps(r.get("status")))
            


