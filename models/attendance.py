from app import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, present, absent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref='attendance_record')
    
    def mark_present(self):
        """Mark user as present"""
        self.status = 'present'
        self.check_in_time = datetime.utcnow()
        db.session.commit()
    
    def mark_absent(self):
        """Mark user as absent"""
        self.status = 'absent'
        db.session.commit()
    
    def check_out(self):
        """Record check out time"""
        self.check_out_time = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<Attendance {self.id}>'
