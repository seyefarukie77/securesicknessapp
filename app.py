#app.py
from flask import Flask
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from routes import sickness_bp
from model import User


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
if os.environ.get("INIT_DB") == "true":
    with app.app_context():
        db.create_all()

    # Demo users
    employee = User(name="Alice Employee", role="employee")
    manager = User(name="Bob Manager", role="manager")

    db.session.add_all([employee, manager])
    db.session.commit()

    print("Database initialised.")
