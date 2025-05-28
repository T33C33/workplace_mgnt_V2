from app import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)
    timeframe_id = db.Column(db.Integer, db.ForeignKey('timeframes.id'), nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled
    notes = db.Column(db.Text)
    
    # Unique constraint to prevent double booking
    __table_args__ = (
        db.UniqueConstraint('seat_id', 'timeframe_id', name='unique_seat_timeframe'),
        db.UniqueConstraint('user_id', 'timeframe_id', name='unique_user_timeframe')
    )
    
    def expire_booking(self):
        """Mark booking as expired"""
        self.status = 'expired'
        db.session.commit()
    
    def cancel_booking(self):
        """Cancel booking"""
        self.status = 'cancelled'
        db.session.commit()
    
    def __repr__(self):
        return f'<Booking {self.id}>'
