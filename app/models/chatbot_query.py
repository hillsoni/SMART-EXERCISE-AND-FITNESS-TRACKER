from app import db
from datetime import datetime

class ChatbotQuery(db.Model):
    __tablename__ = 'chatbot_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    query_type = db.Column(db.String(50))  # diet, workout, yoga, general
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
