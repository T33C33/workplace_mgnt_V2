from app import db
from datetime import datetime

class Hall(db.Model):
    __tablename__ = 'halls'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    workplace_id = db.Column(db.Integer, db.ForeignKey('workplaces.id'), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    seats = db.relationship('Seat', backref='hall', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Hall {self.name}>'
