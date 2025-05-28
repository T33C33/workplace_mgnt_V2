from flask import Blueprint, jsonify
from flask_login import login_required
from models import *
from datetime import date

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/api/seats/<int:timeframe_id>')
@login_required
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

@booking_bp.route('/api/halls/<int:workplace_id>')
@login_required
def get_halls_by_workplace(workplace_id):
    halls = Hall.query.filter_by(workplace_id=workplace_id, is_active=True).all()
    halls_data = []
    
    for hall in halls:
        halls_data.append({
            'id': hall.id,
            'name': hall.name,
            'capacity': hall.capacity
        })
    
    return jsonify(halls_data)

@booking_bp.route('/api/seats-by-hall/<int:hall_id>/<int:timeframe_id>')
@login_required
def get_seats_by_hall(hall_id, timeframe_id):
    hall = Hall.query.get_or_404(hall_id)
    seats_data = []
    
    for seat in hall.seats:
        if seat.is_active:
            seats_data.append({
                'id': seat.id,
                'seat_number': seat.seat_number,
                'available': seat.is_available(timeframe_id)
            })
    
    return jsonify(seats_data)
