from sqlalchemy.orm import Session
from core.models import Excercise, Muscle, ExcerciseMuscle
from sqlalchemy.orm import Session
from core.utils import get_db
from core.config import SessionLocal

def seed():
    db = SessionLocal()
    excercice_muscle = {"Push-ups": ["Triceps", "Deltoids", "Pectorals", "Rectus Abdominis", "Obliques"], "Sit-ups": ["Rectus Abdominis", "Obliques"], "Squats": ["Gluteus Maximus", "Quadriceps", "Hamstrings", "Calves"], "Lunges": ["Gluteus Maximus", "Quadriceps", "Hamstrings", "Calves"], "Pull-ups": ["Latissimus Dorsi", "Biceps", "Trapezius", "Rhomboids"], "Bench Press": ["Pectorals", "Triceps", "Deltoids"], "Deadlift": ["Gluteus Maximus", "Quadriceps", "Hamstrings", "Erector Spinae"], "Overhead Press": ["Deltoids", "Triceps"], "Barbell Row": ["Latissimus Dorsi", "Biceps", "Trapezius", "Rhomboids"], "Upright Row": ["Deltoids", "Triceps", "Trapezius", "Rhomboids"], "Dips": ["Triceps", "Pectorals", "Deltoids"], "Bicep Curls": ["Biceps"], "Tricep Extensions": ["Triceps"], "Leg Press": ["Gluteus Maximus", "Quadriceps", "Hamstrings", "Calves"], "Calf Raises": ["Calves"], "Shoulder Press": ["Deltoids", "Triceps"], "Lat Pulldowns": ["Latissimus Dorsi", "Biceps", "Trapezius", "Rhomboids"], "Bent Over Rows": ["Latissimus Dorsi", "Biceps", "Trapezius", "Rhomboids"], "Pec Deck Fly": ["Pectorals"], "Lateral Raise": ["Deltoids"]}

    # now we need to create the excercises and muscles and then link them together
    for excercise, muscles in excercice_muscle.items():
        excercise = Excercise(name=excercise, description="Description for " + excercise, instructions="Instructions for " + excercise)
        db.add(excercise)
        db.commit()
        for muscle in muscles:
            muscle = Muscle(name=muscle)
            db.add(muscle)
            db.commit()
            excercise_muscle = ExcerciseMuscle(excercise_id=excercise.id, muscle_id=muscle.id)
            db.add(excercise_muscle)
        db.commit()

    db.commit()

def clear():
    db = SessionLocal()
    db.query(ExcerciseMuscle).delete()
    db.query(Excercise).delete()
    db.query(Muscle).delete()
    db.commit()
    db.close()