from app import db
from datetime import datetime
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    mobile_number = db.Column(db.String(15))
    height = db.Column(db.Float)  # Height in cm
    weight = db.Column(db.Float)  # Weight in kg
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    diet_plans = db.relationship('DietPlan', backref='user', lazy=True)
    exercise_plans = db.relationship('ExercisePlan', backref='user', lazy=True)
    chatbot_queries = db.relationship('ChatbotQuery', backref='user', lazy=True)
    user_challenges = db.relationship('UserChallenge', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
