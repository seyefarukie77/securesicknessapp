from flask import Flask, jsonify, render_template, request, redirect, url_for
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from routes import sickness_bp
from model import User, SicknessRecord
import click
from flask.cli import with_appcontext


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///sickness.db"
)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["UPLOAD_FOLDER"] = "uploads"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(sickness_bp, url_prefix="/api/sickness")

    return app


app = create_app()


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        # existing logic (save record)
        return redirect(url_for("records"))
    return render_template("submit.html")


@app.route("/records")
def records():
    data = SicknessRecord.query.all()  # from your model/database
    return render_template("records.html", records=data)


if os.environ.get("INIT_DB") == "true":
    with app.app_context():
        db.create_all()
    print("Database initialised.")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 8000)),
        debug=False
    )
    
