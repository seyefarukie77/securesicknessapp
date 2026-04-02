#app.py
from flask import Flask
from database import db
from routes import sickness_bp
import os

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sickness.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = "uploads"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(sickness_bp, url_prefix="/api/sickness")

    return app

app = create_app()

# Flask CLI command
with app.app_context():
    from models import User
    db.drop_all()
    db.create_all()

    # Demo users
    employee = User(name="Alice Employee", role="employee")
    manager = User(name="Bob Manager", role="manager")

    db.session.add_all([employee, manager])
    db.session.commit()

    print("Database initialised.")

