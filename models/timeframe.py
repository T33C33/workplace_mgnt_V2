from app import db
from datetime import datetime, time

class TimeFrame(db.Model):
    __tablename__ = 'timeframes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    max_users = db.Column(db.Integer, default=50)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='timeframe', lazy=True)
    
    def is_expired(self):
        """Check if timeframe has expired"""
        now = datetime.now()
        timeframe_end = datetime.combine(self.date, self.end_time)
        return now > timeframe_end
    
    def get_current_bookings_count(self):
        """Get number of active bookings for this timeframe"""
        from models.booking import Booking
        return Booking.query.filter_by(
            timeframe_id=self.id,
            status='active'
        ).count()
    
    def can_accept_more_bookings(self):
        """Check if timeframe can accept more bookings"""
        return self.get_current_bookings_count() < self.max_users
    
    def __repr__(self):
        return f'<TimeFrame {self.name}>'
