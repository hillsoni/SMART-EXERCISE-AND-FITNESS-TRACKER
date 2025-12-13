from app import db

class Yoga(db.Model):
    __tablename__ = 'yoga'
    
    id = db.Column(db.Integer, primary_key=True)
    yoga_name = db.Column(db.String(100), nullable=False)
    yoga_description = db.Column(db.Text)
    photo_url = db.Column(db.String(500), unique=True)  # MinIO URL
    difficulty_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    duration_minutes = db.Column(db.Integer)
    benefits = db.Column(db.Text)