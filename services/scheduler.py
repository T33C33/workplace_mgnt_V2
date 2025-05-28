from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models import *
from app import db
from services.email_service import send_expiry_notification, send_admin_notification

def check_expired_bookings():
    """Check for expired bookings and send notifications"""
    with db.app.app_context():
        # Get all active bookings with expired timeframes
        expired_bookings = db.session.query(Booking, User, Seat, Hall, Workplace, TimeFrame).join(
            User, Booking.user_id == User.id
        ).join(
            Seat, Booking.seat_id == Seat.id
        ).join(
            Hall, Seat.hall_id == Hall.id
        ).join(
            Workplace, Hall.workplace_id == Workplace.id
        ).join(
            TimeFrame, Booking.timeframe_id == TimeFrame.id
        ).filter(
            Booking.status == 'active'
        ).all()
        
        for booking, user, seat, hall, workplace, timeframe in expired_bookings:
            if timeframe.is_expired():
                # Mark booking as expired
                booking.expire_booking()
                
                # Send expiry notification to user
                send_expiry_notification(user, booking, seat, hall, workplace, timeframe)
                
                # Send notification to admin
                admin_users = User.query.filter_by(is_admin=True).all()
                for admin in admin_users:
                    send_admin_notification(
                        admin.email,
                        "Booking Expired",
                        f"Booking {booking.id} for {user.full_name} has expired. "
                        f"Seat {seat.seat_number} in {hall.name} is now available."
                    )

def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Check for expired bookings every 5 minutes
    scheduler.add_job(
        func=check_expired_bookings,
        trigger="interval",
        minutes=5,
        id='check_expired_bookings'
    )
    
    scheduler.start()
    return scheduler
