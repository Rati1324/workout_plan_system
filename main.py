import json, asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from sqlalchemy_utils import database_exists, create_database
from core.utils import get_db, get_current_user
from core.models import User, Exercise, WorkoutPlan, ExerciseWorkout, Goal, WeightTracker, Muscle, ExerciseMuscle
from core.config import SessionLocal, engine, Base
from core.schemas import WorkoutPlanSchema, GoalSchema, WeightTrackerSchema, GetExerciseSchema
from core.services import get_workout_plans_db
from datetime import datetime
from core.services import router as services
from core.session_tracking import router as session_tracking
from seed_db import seed, clear

app = FastAPI()

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database created.")

# Base.metadata.create_all(bind=engine)
# seed()
# clear()

app.include_router(services)
app.include_router(session_tracking)

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

@app.post("/edit_plan")
async def edit_plan(dependencies = Depends(get_current_user), db: Session = Depends(get_db), workout_plan: WorkoutPlanSchema = None):
    db_workout_plan = db.query(WorkoutPlan).filter_by(id=workout_plan.id).first()
    if db_workout_plan is None:
        raise HTTPException(status_code=400, detail="Plan not found")

    if db_workout_plan.user_id != dependencies.id:
        raise HTTPException(status_code=400, detail="You are not the owner of this plan")

    db_workout_plan.name = workout_plan.name
    db_workout_plan.weekdays = workout_plan.weekdays
    db_workout_plan.duration = workout_plan.duration
    db_workout_plan.goals = workout_plan.goals

    db.query(ExerciseWorkout).filter_by(workout_id=workout_plan.id).delete()
    db.commit()

    last_order_num = 0
    for exercise in workout_plan.exercises:
        if exercise.order != last_order_num + 1:
            raise HTTPException(status_code=400, detail="Order of exercises is not correct")
        last_order_num = exercise.order

        db_exercise_workout = ExerciseWorkout(
            exercise_id = exercise.id,
            workout_id = workout_plan.id,
            repetitions = exercise.repetitions,
            sets = exercise.sets,
            break_between_sets = exercise.break_between_sets,
            break_after_exercise = exercise.break_after_exercise,
            order = exercise.order,
        )
        db_workout_plan.exercises.append(db_exercise_workout)
        db.add(db_exercise_workout)
    db.commit()
    return {"response": "edited successfully"}

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

@app.get("/get_workout_plans")
async def get_workout_plans(dependencies = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = dependencies.id
    workout_plans = await get_workout_plans_db(db, user_id)
    return workout_plans

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
async def get_exercises(dependencies = Depends(get_current_user), db: Session = Depends(get_db), exercise_data: GetExerciseSchema = None):
    if exercise_data is not None:
        if exercise_data.name is not None:
            exercises = db.query(Exercise).filter(Exercise.name.ilike(f"%{exercise_data.name}%")).all()

        elif exercise_data.muscles is not None:
            exercises = db.query(Exercise).join(Exercise.exercise_muscles).join(Muscle).filter(or_(*[Muscle.name.like(f"%{m}%") for m in exercise_data.muscles])).all()
    else:
        exercises = db.query(Exercise).all()

    return exercises