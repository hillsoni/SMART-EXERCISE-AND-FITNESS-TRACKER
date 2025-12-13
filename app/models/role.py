from app import db

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    # Relationships
    users = db.relationship('User', backref='role', lazy=True)
