from app import db
from datetime import datetime

class Workplace(db.Model):
    __tablename__ = 'workplaces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    halls = db.relationship('Hall', backref='workplace', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Workplace {self.name}>'
