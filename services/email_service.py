from flask_mail import Message
from app import mail
from flask import current_app
import threading

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

def send_email(subject, recipients, html_body, text_body=None):
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=html_body,
        body=text_body
    )
    
    # Send email asynchronously
    thread = threading.Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    )
    thread.start()

def send_booking_confirmation(user, booking, seat, hall, workplace, timeframe):
    subject = f"Seat Booking Confirmation - {workplace.name}"
    
    html_body = f"""
    <html>
    <body>
        <h2>Booking Confirmation</h2>
        <p>Dear {user.full_name},</p>
        
        <p>Your seat booking has been confirmed with the following details:</p>
        
        <table border="1" cellpadding="10" cellspacing="0">
            <tr><td><strong>Workplace:</strong></td><td>{workplace.name}</td></tr>
            <tr><td><strong>Hall:</strong></td><td>{hall.name}</td></tr>
            <tr><td><strong>Seat Number:</strong></td><td>{seat.seat_number}</td></tr>
            <tr><td><strong>Date:</strong></td><td>{timeframe.date}</td></tr>
            <tr><td><strong>Time:</strong></td><td>{timeframe.start_time} - {timeframe.end_time}</td></tr>
            <tr><td><strong>Booking ID:</strong></td><td>{booking.id}</td></tr>
        </table>
        
        <p><strong>Important Notes:</strong></p>
        <ul>
            <li>Please arrive on time for your booking</li>
            <li>Your booking will expire at {timeframe.end_time} on {timeframe.date}</li>
            <li>You will receive a notification when your booking expires</li>
        </ul>
        
        <p>Thank you for using our workplace management system!</p>
        
        <p>Best regards,<br>
        Workplace Management Team</p>
    </body>
    </html>
    """
    
    text_body = f"""
    Booking Confirmation
    
    Dear {user.full_name},
    
    Your seat booking has been confirmed:
    
    Workplace: {workplace.name}
    Hall: {hall.name}
    Seat Number: {seat.seat_number}
    Date: {timeframe.date}
    Time: {timeframe.start_time} - {timeframe.end_time}
    Booking ID: {booking.id}
    
    Please arrive on time. Your booking expires at {timeframe.end_time} on {timeframe.date}.
    
    Best regards,
    Workplace Management Team
    """
    
    send_email(subject, [user.email], html_body, text_body)

def send_expiry_notification(user, booking, seat, hall, workplace, timeframe):
    subject = f"Seat Booking Expired - {workplace.name}"
    
    html_body = f"""
    <html>
    <body>
        <h2>Booking Expiry Notification</h2>
        <p>Dear {user.full_name},</p>
        
        <p>Your seat booking has expired:</p>
        
        <table border="1" cellpadding="10" cellspacing="0">
            <tr><td><strong>Workplace:</strong></td><td>{workplace.name}</td></tr>
            <tr><td><strong>Hall:</strong></td><td>{hall.name}</td></tr>
            <tr><td><strong>Seat Number:</strong></td><td>{seat.seat_number}</td></tr>
            <tr><td><strong>Date:</strong></td><td>{timeframe.date}</td></tr>
            <tr><td><strong>Time:</strong></td><td>{timeframe.start_time} - {timeframe.end_time}</td></tr>
            <tr><td><strong>Booking ID:</strong></td><td>{booking.id}</td></tr>
        </table>
        
        <p>The seat is now available for other bookings.</p>
        
        <p>Thank you for using our workplace management system!</p>
        
        <p>Best regards,<br>
        Workplace Management Team</p>
    </body>
    </html>
    """
    
    send_email(subject, [user.email], html_body)

def send_admin_notification(admin_email, subject, message):
    """Send notification to admin"""
    html_body = f"""
    <html>
    <body>
        <h2>Admin Notification</h2>
        <p>{message}</p>
        
        <p>Best regards,<br>
        Workplace Management System</p>
    </body>
    </html>
    """
    
    send_email(subject, [admin_email], html_body)
