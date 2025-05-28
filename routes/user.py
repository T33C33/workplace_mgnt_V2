from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import *
from app import db
from datetime import date
from services.email_service import send_booking_confirmation

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's active bookings
    user_bookings = db.session.query(Booking, Seat, Hall, Workplace, TimeFrame).join(
        Seat, Booking.seat_id == Seat.id
    ).join(
        Hall, Seat.hall_id == Hall.id
    ).join(
        Workplace, Hall.workplace_id == Workplace.id
    ).join(
        TimeFrame, Booking.timeframe_id == TimeFrame.id
    ).filter(
        Booking.user_id == current_user.id,
        Booking.status == 'active'
    ).order_by(TimeFrame.date.desc()).all()
    
    # Get user's attendance records
    attendance_records = db.session.query(Attendance, Booking, Seat, Hall, TimeFrame).join(
        Booking, Attendance.booking_id == Booking.id
    ).join(
        Seat, Booking.seat_id == Seat.id
    ).join(
        Hall, Seat.hall_id == Hall.id
    ).join(
        TimeFrame, Booking.timeframe_id == TimeFrame.id
    ).filter(
        Attendance.user_id == current_user.id
    ).order_by(Attendance.created_at.desc()).limit(10).all()
    
    return render_template('user/dashboard.html', 
                         user_bookings=user_bookings,
                         attendance_records=attendance_records)

@user_bp.route('/book-seat', methods=['GET', 'POST'])
@login_required
def book_seat():
    if request.method == 'POST':
        timeframe_id = request.form['timeframe_id']
        seat_id = request.form['seat_id']
        
        # Check if user already has a booking for this timeframe
        existing_booking = Booking.query.filter_by(
            user_id=current_user.id,
            timeframe_id=timeframe_id,
            status='active'
        ).first()
        
        if existing_booking:
            flash('You already have a booking for this timeframe!', 'error')
            return redirect(url_for('user.book_seat'))
        
        # Check if timeframe can accept more bookings
        timeframe = TimeFrame.query.get(timeframe_id)
        if not timeframe.can_accept_more_bookings():
            flash('This timeframe is fully booked!', 'error')
            return redirect(url_for('user.book_seat'))
        
        # Check if seat is available
        seat = Seat.query.get(seat_id)
        if not seat.is_available(timeframe_id):
            flash('Seat is not available for this timeframe!', 'error')
            return redirect(url_for('user.book_seat'))
        
        # Create booking
        booking = Booking(
            user_id=current_user.id,
            seat_id=seat_id,
            timeframe_id=timeframe_id
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Create attendance record
        attendance = Attendance(
            user_id=current_user.id,
            booking_id=booking.id
        )
        db.session.add(attendance)
        db.session.commit()
        
        # Send confirmation email
        hall = seat.hall
        workplace = hall.workplace
        
        send_booking_confirmation(current_user, booking, seat, hall, workplace, timeframe)
        
        flash('Seat booked successfully! Check your email for confirmation.', 'success')
        return redirect(url_for('user.dashboard'))
    
    # Get available timeframes (future dates only)
    timeframes = TimeFrame.query.filter_by(is_active=True).filter(
        TimeFrame.date >= date.today()
    ).all()
    
    workplaces = Workplace.query.filter_by(is_active=True).all()
    
    return render_template('user/book_seat.html', timeframes=timeframes, workplaces=workplaces)

@user_bp.route('/my-bookings')
@login_required
def my_bookings():
    bookings = db.session.query(Booking, Seat, Hall, Workplace, TimeFrame).join(
        Seat, Booking.seat_id == Seat.id
    ).join(
        Hall, Seat.hall_id == Hall.id
    ).join(
        Workplace, Hall.workplace_id == Workplace.id
    ).join(
        TimeFrame, Booking.timeframe_id == TimeFrame.id
    ).filter(
        Booking.user_id == current_user.id
    ).order_by(Booking.booking_time.desc()).all()
    
    return render_template('user/my_bookings.html', bookings=bookings)

@user_bp.route('/attendance')
@login_required
def attendance():
    attendance_records = db.session.query(Attendance, Booking, Seat, Hall, TimeFrame).join(
        Booking, Attendance.booking_id == Booking.id
    ).join(
        Seat, Booking.seat_id == Seat.id
    ).join(
        Hall, Seat.hall_id == Hall.id
    ).join(
        TimeFrame, Booking.timeframe_id == TimeFrame.id
    ).filter(
        Attendance.user_id == current_user.id
    ).order_by(Attendance.created_at.desc()).all()
    
    return render_template('user/attendance.html', attendance_records=attendance_records)

@user_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.filter_by(
        id=booking_id,
        user_id=current_user.id,
        status='active'
    ).first_or_404()
    
    booking.cancel_booking()
    flash('Booking cancelled successfully!', 'success')
    return redirect(url_for('user.my_bookings'))
