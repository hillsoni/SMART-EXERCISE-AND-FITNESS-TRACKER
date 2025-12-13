from app import db
from datetime import datetime

class DietPlan(db.Model):
    __tablename__ = 'diet_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    diet_plan = db.Column(db.JSON, nullable=False)  # JSONB in PostgreSQL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    goal = db.Column(db.String(50))
    diet_type = db.Column(db.String(50))
    duration = db.Column(db.String(50))