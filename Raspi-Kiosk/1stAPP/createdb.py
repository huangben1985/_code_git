from app import app,db

with app.app_context():  # Ensure we're inside an app context
    db.create_all()  # Create tables if they don't exist