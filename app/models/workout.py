from app import db

class Workout(db.Model):
    __tablename__ = 'workouts'
    
    id = db.Column(db.Integer, primary_key=True)
    workout_name = db.Column(db.String(100), nullable=False)
    workout_description = db.Column(db.Text)
    category = db.Column(db.String(50))  # strength, cardio, flexibility
    difficulty_level = db.Column(db.String(20))
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    equipment_needed = db.Column(db.Text)
    photo_url = db.Column(db.String(500))