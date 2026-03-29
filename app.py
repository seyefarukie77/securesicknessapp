# app.py
import os
from datetime import datetime
from uuid import uuid4

from flask import Flask, request, jsonify, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sickness.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class User(db.Model):
    """
    Very simple user model.
    In a real system, you'd integrate with your IdP/HR system instead.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "employee" or "manager"


class SicknessReport(db.Model):
    __tablename__ = "sickness_reports"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    full_day = db.Column(db.Boolean, nullable=False, default=True)
    reason = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending/approved/rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # optional document path
    document_path = db.Column(db.String(255), nullable=True)

    employee = db.relationship("User", backref="sickness_reports")


# -----------------------------------------------------------------------------
# Helpers: simple "auth" via headers (for demo)
# -----------------------------------------------------------------------------
def get_current_user():
    """
    Simulate auth using headers:
      X-User-Id: 1
      X-User-Role: employee|manager
    In real life, replace with JWT / SSO / etc.
    """
    user_id = request.headers.get("X-User-Id")
    role = request.headers.get("X-User-Role")

    if not user_id or not role:
        abort(401, description="Missing X-User-Id or X-User-Role headers")

    user = User.query.get(user_id)
    if not user:
        abort(401, description="User not found")

    if user.role != role:
        abort(403, description="Role mismatch")

    return user


def parse_date(value, field_name):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        abort(400, description=f"Invalid date format for {field_name}, expected YYYY-MM-DD")


# -----------------------------------------------------------------------------
# Routes: Setup / bootstrap
# -----------------------------------------------------------------------------
@app.cli.command("init-db")
def init_db():
    """Initialize the database and create some demo users."""
    db.drop_all()
    db.create_all()

    # Demo users
    employee = User(name="Alice Employee", role="employee")
    manager = User(name="Bob Manager", role="manager")
    db.session.add_all([employee, manager])
    db.session.commit()
    print("Database initialized with demo users:")
    print(f"Employee: id={employee.id}, name={employee.name}")
    print(f"Manager:  id={manager.id}, name={manager.name}")


# -----------------------------------------------------------------------------
# Routes: Employee – create & view own sickness reports
# -----------------------------------------------------------------------------
@app.route("/api/sickness", methods=["POST"])
def create_sickness_report():
    """
    Employee creates a sickness report.
    Accepts multipart/form-data for optional file upload.
    Fields:
      start_date (YYYY-MM-DD)
      end_date   (YYYY-MM-DD)
      full_day   (true/false)
      reason     (string)
      document   (file, optional)
    """
    user = get_current_user()
    if user.role != "employee":
        abort(403, description="Only employees can create sickness reports")

    # For file upload, use form instead of JSON
    start_date_str = request.form.get("start_date")
    end_date_str = request.form.get("end_date")
    full_day_str = request.form.get("full_day", "true")
    reason = request.form.get("reason")

    if not start_date_str or not end_date_str or not reason:
        abort(400, description="start_date, end_date and reason are required")

    start_date = parse_date(start_date_str, "start_date")
    end_date = parse_date(end_date_str, "end_date")
    full_day = full_day_str.lower() in ("true", "1", "yes")

    if end_date < start_date:
        abort(400, description="end_date cannot be before start_date")

    # Handle optional document upload
    document_path = None
    if "document" in request.files:
        file = request.files["document"]
        if file.filename:
            filename = secure_filename(file.filename)
            # Add a UUID prefix to avoid collisions
            filename = f"{uuid4().hex}_{filename}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            document_path = filename

    report = SicknessReport(
        employee_id=user.id,
        start_date=start_date,
        end_date=end_date,
        full_day=full_day,
        reason=reason,
        status="pending",
        document_path=document_path,
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({
        "id": report.id,
        "employee_id": report.employee_id,
        "start_date": report.start_date.isoformat(),
        "end_date": report.end_date.isoformat(),
        "full_day": report.full_day,
        "reason": report.reason,
        "status": report.status,
        "document_path": report.document_path,
        "created_at": report.created_at.isoformat(),
    }), 201


@app.route("/api/sickness/my", methods=["GET"])
def list_my_sickness_reports():
    """Employee views their own sickness reports."""
    user = get_current_user()
    if user.role != "employee":
        abort(403, description="Only employees can view their own sickness reports")

    reports = SicknessReport.query.filter_by(employee_id=user.id).order_by(SicknessReport.created_at.desc()).all()
    return jsonify([
        {
            "id": r.id,
            "start_date": r.start_date.isoformat(),
            "end_date": r.end_date.isoformat(),
            "full_day": r.full_day,
            "reason": r.reason,
            "status": r.status,
            "document_path": r.document_path,
            "created_at": r.created_at.isoformat(),
        }
        for r in reports
    ])


# -----------------------------------------------------------------------------
# Routes: Manager – review & approve/reject
# -----------------------------------------------------------------------------
@app.route("/api/sickness", methods=["GET"])
def list_all_sickness_reports():
    """Manager lists all sickness reports."""
    user = get_current_user()
    if user.role != "manager":
        abort(403, description="Only managers can list all sickness reports")

    status_filter = request.args.get("status")  # optional ?status=pending
    query = SicknessReport.query.join(User, SicknessReport.employee)

    if status_filter:
        query = query.filter(SicknessReport.status == status_filter)

    reports = query.order_by(SicknessReport.created_at.desc()).all()
    return jsonify([
        {
            "id": r.id,
            "employee_id": r.employee_id,
            "employee_name": r.employee.name,
            "start_date": r.start_date.isoformat(),
            "end_date": r.end_date.isoformat(),
            "full_day": r.full_day,
            "reason": r.reason,
            "status": r.status,
            "document_path": r.document_path,
            "created_at": r.created_at.isoformat(),
        }
        for r in reports
    ])


@app.route("/api/sickness/<int:report_id>/status", methods=["PATCH"])
def update_sickness_status(report_id):
    """
    Manager approves or rejects a sickness report.
    Body (JSON):
      { "status": "approved" } or { "status": "rejected" }
    """
    user = get_current_user()
    if user.role != "manager":
        abort(403, description="Only managers can update sickness status")

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in ("approved", "rejected"):
        abort(400, description="status must be 'approved' or 'rejected'")

    report = SicknessReport.query.get_or_404(report_id)
    report.status = new_status
    db.session.commit()

    return jsonify({
        "id": report.id,
        "status": report.status,
    })


# -----------------------------------------------------------------------------
# Routes: Document download (manager or owner)
# -----------------------------------------------------------------------------
@app.route("/api/sickness/<int:report_id>/document", methods=["GET"])
def download_document(report_id):
    """
    Download the supporting document for a sickness report.
    Only:
      - the employee who created it, or
      - a manager
    can access it.
    """
    user = get_current_user()
    report = SicknessReport.query.get_or_404(report_id)

    if not report.document_path:
        abort(404, description="No document attached to this report")

    if user.role != "manager" and user.id != report.employee_id:
        abort(403, description="Not allowed to access this document")

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        report.document_path,
        as_attachment=True,
    )


# -----------------------------------------------------------------------------
# Error handlers
# -----------------------------------------------------------------------------
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "bad_request", "message": str(e.description)}), 400


@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "unauthorized", "message": str(e.description)}), 401


@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "forbidden", "message": str(e.description)}), 403


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not_found", "message": str(e.description)}), 404


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # For local dev; in CI/CD you’ll run via gunicorn/uwsgi, etc.
    app.run(host="0.0.0.0", port=8000, debug=True)
