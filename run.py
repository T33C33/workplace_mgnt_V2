from app import create_app, db
from services.scheduler import start_scheduler
import os

app = create_app()

# Start the background scheduler for checking expired bookings
scheduler = start_scheduler()

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Create default admin user if it doesn't exist
        from models.user import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@workplace.com',
                full_name='System Administrator',
                phone_number='+2348012345678',
                is_admin=True
            )
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
