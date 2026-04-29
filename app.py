from flask import Flask, jsonify, render_template, redirect, url_for, request
import os
from database import db
from model import SicknessRecord
from routes import sickness_bp
import click
from flask.cli import with_appcontext
import sys


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:////tmp/sickness.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    app.register_blueprint(sickness_bp, url_prefix="/api/sickness")
    return app


app = create_app()


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        with app.app_context():
            record = SicknessRecord(
                employee_id=int(request.form["employee_id"]),
                start_date=__import__("datetime").datetime.strptime(
                    request.form["start_date"], "%Y-%m-%d"
                ).date(),
                end_date=__import__("datetime").datetime.strptime(
                    request.form["end_date"], "%Y-%m-%d"
                ).date(),
                reason=request.form["reason"],
            )
            db.session.add(record)
            db.session.commit()
        return redirect(url_for("home"))
    return render_template("submit.html")


@app.route("/records")
def records():
    all_records = SicknessRecord.query.order_by(
        SicknessRecord.start_date.desc()
    ).all()
    return render_template("records.html", records=all_records)


@app.cli.command("init-db")
def init_db_command():
    db.create_all()
    print("Database initialised.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
