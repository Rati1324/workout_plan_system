from sqlalchemy.orm import Session
from core.models import Exercise, Muscle, ExerciseMuscle
from sqlalchemy.orm import Session
from core.utils import get_db
from core.config import SessionLocal

def seed():
    db = SessionLocal()
    excercice_muscle = {"Push-ups": ["Triceps", "Deltoids", "Pectorals", "Rectus Abdominis", "Obliques"], "Sit-ups": ["Rectus Abdominis", "Obliques"], "Squats": ["Gluteus Maximus", "Quadriceps", "Hamstrings", "Calves"], "Lunges": ["Gluteus Maximus", "Quadriceps", "Hamstrings", "Calves"], "Pull-ups": ["Latissimus Dorsi", "Biceps", "Trapezius", "Rhomboids"], "Bench Press": ["Pectorals", "Triceps", "Deltoids"], "Deadlift": ["Gluteus Maximus", "Quadriceps", "Hamstrings", "Erector Spinae"], "Overhead Press": ["Deltoids", "Triceps"], "Barbell Row": ["Latissimus Dorsi", "Biceps", "Trapezius", "Rhomboids"], "Upright Row": ["Deltoids", "Triceps", "Trapezius", "Rhomboids"], "Dips": ["Triceps", "Pectorals", "Deltoids"], "Bicep Curls": ["Biceps"], "Tricep Extensions": ["Triceps"], "Leg Press": ["Gluteus Maximus", "Quadriceps", "Hamstrings", "Calves"], "Calf Raises": ["Calves"], "Shoulder Press": ["Deltoids", "Triceps"], "Lat Pulldowns": ["Latissimus Dorsi", "Biceps", "Trapezius", "Rhomboids"], "Bent Over Rows": ["Latissimus Dorsi", "Biceps", "Trapezius", "Rhomboids"], "Pec Deck Fly": ["Pectorals"], "Lateral Raise": ["Deltoids"]}

    # now we need to create the exercises and muscles and then link them together
    for exercise, muscles in excercice_muscle.items():
        exercise = Exercise(name=exercise, description="Description for " + exercise, instructions="Instructions for " + exercise)
        db.add(exercise)
        db.commit()
        for muscle in muscles:
            muscle = Muscle(name=muscle)
            db.add(muscle)
            db.commit()
            exercise_muscle = ExerciseMuscle(exercise_id=exercise.id, muscle_id=muscle.id)
            db.add(exercise_muscle)
        db.commit()

    db.commit()

def clear():
    db = SessionLocal()
    db.query(ExerciseMuscle).delete()
    db.query(Exercise).delete()
    db.query(Muscle).delete()
    db.commit()
    db.close()

#     {
#   "name": "string",
#   "frequency": 0,
#   "duration": 0,
#   "goals": "string",
#   "exercises": [
#     {
#       "id": 1,
#       "repetitions": 3,
#       "sets": 1,
#       "order": 1,
#       "break_time": 60
#     },
#     {
#       "id": 2,
#       "repetitions": 2,
#       "sets": 2,
#       "order": 2,
#       "break_time": 60
#     }
#   ]
# }