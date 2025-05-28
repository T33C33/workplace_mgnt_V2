from app import db
from datetime import datetime

class Seat(db.Model):
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(20), nullable=False)
    hall_id = db.Column(db.Integer, db.ForeignKey('halls.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='seat', lazy=True)
    
    # Unique constraint for seat number within a hall
    __table_args__ = (db.UniqueConstraint('seat_number', 'hall_id', name='unique_seat_per_hall'),)
    
    def is_available(self, timeframe_id):
        """Check if seat is available for a specific timeframe"""
        from models.booking import Booking
        existing_booking = Booking.query.filter_by(
            seat_id=self.id,
            timeframe_id=timeframe_id,
            status='active'
        ).first()
        return existing_booking is None
    
    def __repr__(self):
        return f'<Seat {self.seat_number}>'
