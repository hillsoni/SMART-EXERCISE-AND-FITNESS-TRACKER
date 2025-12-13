from app import db
from datetime import datetime

class ExercisePlan(db.Model):
    __tablename__ = 'exercise_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_plan = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    goal = db.Column(db.String(50))
    difficulty_level = db.Column(db.String(20))
    duration_weeks = db.Column(db.Integer)