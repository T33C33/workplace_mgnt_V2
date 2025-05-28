from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import *
from app import db
from datetime import datetime, date, time
from services.email_service import send_booking_confirmation, send_expiry_notification

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_workplaces = Workplace.query.filter_by(is_active=True).count()
    total_bookings = Booking.query.filter_by(status='active').count()
    total_halls = Hall.query.filter_by(is_active=True).count()
    
    # Recent bookings
    recent_bookings = db.session.query(Booking, User, Seat, Hall, Workplace, TimeFrame).join(
        User, Booking.user_id == User.id
    ).join(
        Seat, Booking.seat_id == Seat.id
    ).join(
        Hall, Seat.hall_id == Hall.id
    ).join(
        Workplace, Hall.workplace_id == Workplace.id
    ).join(
        TimeFrame, Booking.timeframe_id == TimeFrame.id
    ).order_by(Booking.booking_time.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_workplaces=total_workplaces,
                         total_bookings=total_bookings,
                         total_halls=total_halls,
                         recent_bookings=recent_bookings)

@admin_bp.route('/workplaces')
@login_required
@admin_required
def workplaces():
    workplaces = Workplace.query.filter_by(is_active=True).all()
    return render_template('admin/workplaces.html', workplaces=workplaces)

@admin_bp.route('/workplaces/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_workplace():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        address = request.form['address']
        
        workplace = Workplace(
            name=name,
            description=description,
            address=address
        )
        
        db.session.add(workplace)
        db.session.commit()
        
        flash('Workplace created successfully!', 'success')
        return redirect(url_for('admin.workplaces'))
    
    return render_template('admin/create_workplace.html')

@admin_bp.route('/workplaces/<int:workplace_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_workplace(workplace_id):
    workplace = Workplace.query.get_or_404(workplace_id)
    
    if request.method == 'POST':
        workplace.name = request.form['name']
        workplace.description = request.form['description']
        workplace.address = request.form['address']
        
        db.session.commit()
        flash('Workplace updated successfully!', 'success')
        return redirect(url_for('admin.workplaces'))
    
    return render_template('admin/edit_workplace.html', workplace=workplace)

@admin_bp.route('/workplaces/<int:workplace_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_workplace(workplace_id):
    workplace = Workplace.query.get_or_404(workplace_id)
    workplace.is_active = False
    db.session.commit()
    flash('Workplace deleted successfully!', 'success')
    return redirect(url_for('admin.workplaces'))

@admin_bp.route('/halls')
@login_required
@admin_required
def halls():
    halls = db.session.query(Hall, Workplace).join(
        Workplace, Hall.workplace_id == Workplace.id
    ).filter(Hall.is_active == True).all()
    return render_template('admin/halls.html', halls=halls)

@admin_bp.route('/halls/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_hall():
    if request.method == 'POST':
        name = request.form['name']
        workplace_id = request.form['workplace_id']
        capacity = int(request.form['capacity'])
        description = request.form['description']
        
        hall = Hall(
            name=name,
            workplace_id=workplace_id,
            capacity=capacity,
            description=description
        )
        
        db.session.add(hall)
        db.session.flush()  # Get the hall ID
        
        # Create seats for the hall
        for i in range(1, capacity + 1):
            seat = Seat(
                seat_number=f"S{i:03d}",
                hall_id=hall.id
            )
            db.session.add(seat)
        
        db.session.commit()
        flash(f'Hall created with {capacity} seats!', 'success')
        return redirect(url_for('admin.halls'))
    
    workplaces = Workplace.query.filter_by(is_active=True).all()
    return render_template('admin/create_hall.html', workplaces=workplaces)

@admin_bp.route('/timeframes')
@login_required
@admin_required
def timeframes():
    timeframes = TimeFrame.query.filter_by(is_active=True).order_by(TimeFrame.date.desc()).all()
    return render_template('admin/timeframes.html', timeframes=timeframes)

@admin_bp.route('/timeframes/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_timeframe():
    if request.method == 'POST':
        name = request.form['name']
        start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        date_str = request.form['date']
        max_users = int(request.form['max_users'])
        
        timeframe = TimeFrame(
            name=name,
            start_time=start_time,
            end_time=end_time,
            date=datetime.strptime(date_str, '%Y-%m-%d').date(),
            max_users=max_users
        )
        
        db.session.add(timeframe)
        db.session.commit()
        
        flash('Time frame created successfully!', 'success')
        return redirect(url_for('admin.timeframes'))
    
    return render_template('admin/create_timeframe.html')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/bookings')
@login_required
@admin_required
def bookings():
    bookings = db.session.query(Booking, User, Seat, Hall, Workplace, TimeFrame).join(
        User, Booking.user_id == User.id
    ).join(
        Seat, Booking.seat_id == Seat.id
    ).join(
        Hall, Seat.hall_id == Hall.id
    ).join(
        Workplace, Hall.workplace_id == Workplace.id
    ).join(
        TimeFrame, Booking.timeframe_id == TimeFrame.id
    ).order_by(Booking.booking_time.desc()).all()
    
    return render_template('admin/bookings.html', bookings=bookings)

@admin_bp.route('/book-seat', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_book_seat():
    if request.method == 'POST':
        timeframe_id = request.form['timeframe_id']
        seat_id = request.form['seat_id']
        
        # Check if admin already has a booking for this timeframe
        existing_booking = Booking.query.filter_by(
            user_id=current_user.id,
            timeframe_id=timeframe_id,
            status='active'
        ).first()
        
        if existing_booking:
            flash('You already have a booking for this timeframe!', 'error')
            return redirect(url_for('admin.admin_book_seat'))
        
        # Check if seat is available
        seat = Seat.query.get(seat_id)
        if not seat.is_available(timeframe_id):
            flash('Seat is not available for this timeframe!', 'error')
            return redirect(url_for('admin.admin_book_seat'))
        
        # Create booking
        booking = Booking(
            user_id=current_user.id,
            seat_id=seat_id,
            timeframe_id=timeframe_id
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Send confirmation email
        timeframe = TimeFrame.query.get(timeframe_id)
        hall = seat.hall
        workplace = hall.workplace
        
        send_booking_confirmation(current_user, booking, seat, hall, workplace, timeframe)
        
        flash('Seat booked successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    # Get available timeframes and seats
    timeframes = TimeFrame.query.filter_by(is_active=True).filter(
        TimeFrame.date >= date.today()
    ).all()
    
    workplaces = Workplace.query.filter_by(is_active=True).all()
    
    return render_template('admin/book_seat.html', timeframes=timeframes, workplaces=workplaces)

@admin_bp.route('/api/seats/<int:timeframe_id>')
@login_required
@admin_required
def get_available_seats(timeframe_id):
    # Get all seats with their availability status
    seats_data = []
    halls = Hall.query.filter_by(is_active=True).all()
    
    for hall in halls:
        for seat in hall.seats:
            if seat.is_active:
                seats_data.append({
                    'id': seat.id,
                    'seat_number': seat.seat_number,
                    'hall_name': hall.name,
                    'workplace_name': hall.workplace.name,
                    'available': seat.is_available(timeframe_id)
                })
    
    return jsonify(seats_data)
