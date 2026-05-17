from app import create_app
from app.extensions import db
from app import models  # important: ensures models are registered

app = create_app()

with app.app_context():
    db.create_all()
    print("PostgreSQL tables created successfully.")