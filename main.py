import json, asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database
from core.utils import get_db, get_hashed_password, create_jwt_token, get_current_user, oauth2_scheme
from core.models import User, Exercise, WorkoutPlan, ExerciseWorkout, Goal, WeightTracker
from core.config import SessionLocal, engine, Base
from core.schemas import UserSchema, WorkoutPlanSchema, GoalSchema, WeightTrackerSchema
from seed_db import seed, clear
from core.user_services import get_workout_plans_db
from datetime import datetime
from core.user_services import router as user_services

app = FastAPI()

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database created.")

# Base.metadata.create_all(bind=engine)
# seed()
# clear()

app.include_router(user_services)

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

@app.get("/get_workout_plans")
async def get_workout_plans(dependencies = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = dependencies.id
    workout_plans = get_workout_plans_db(db, user_id)
    return workout_plans

