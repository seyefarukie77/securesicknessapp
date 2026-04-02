import os
from uuid import uuid4
from datetime import datetime
from flask import Blueprint, request, jsonify, abort, send_from_directory
from werkzeug.utils import secure_filename
from database import db
from model import User, SicknessReport

sickness_bp = Blueprint("sickness", __name__)

def get_user():
    user_id = request.headers.get("X-User-Id")
    role = request.headers.get("X-User-Role")

    if not user_id or not role:
        abort(401, "Missing auth headers")

    user = User.query.get(user_id)
    if not user or user.role != role:
        abort(403, "Invalid user or role")

    return user

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()

@sickness_bp.route("/", methods=["POST"])
def create_report():
    user = get_user()
    if user.role != "employee":
        abort(403)

    form = request.form
    start_date = parse_date(form["start_date"])
    end_date = parse_date(form["end_date"])
    full_day = form.get("full_day", "true").lower() == "true"
    reason = form["reason"]

    document_path = None
    if "document" in request.files:
        file = request.files["document"]
        if file.filename:
            filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
            file.save(os.path.join("uploads", filename))
            document_path = filename

    report = SicknessReport(
        employee_id=user.id,
        start_date=start_date,
        end_date=end_date,
        full_day=full_day,
        reason=reason,
        document_path=document_path
    )

    db.session.add(report)
    db.session.commit()

    return jsonify({"message": "Report submitted", "id": report.id}), 201

@sickness_bp.route("/my", methods=["GET"])
def my_reports():
    user = get_user()
    reports = SicknessReport.query.filter_by(employee_id=user.id).all()
    return jsonify([{
        "id": r.id,
        "start_date": r.start_date.isoformat(),
        "end_date": r.end_date.isoformat(),
        "reason": r.reason,
        "status": r.status
    } for r in reports])

@sickness_bp.route("/", methods=["GET"])
def all_reports():
    user = get_user()
    if user.role != "manager":
        abort(403)

    reports = SicknessReport.query.all()
    return jsonify([{
        "id": r.id,
        "employee": r.employee.name,
        "start_date": r.start_date.isoformat(),
        "end_date": r.end_date.isoformat(),
        "reason": r.reason,
        "status": r.status
    } for r in reports])

@sickness_bp.route("/<int:id>/status", methods=["PATCH"])
def update_status(id):
    user = get_user()
    if user.role != "manager":
        abort(403)

    report = SicknessReport.query.get_or_404(id)
    new_status = request.json.get("status")

    if new_status not in ("approved", "rejected"):
        abort(400, "Invalid status")

    report.status = new_status
    db.session.commit()

    return jsonify({"message": "Status updated"})

@sickness_bp.route("/<int:id>/document", methods=["GET"])
def download(id):
    user = get_user()
    report = SicknessReport.query.get_or_404(id)

    if user.role != "manager" and user.id != report.employee_id:
        abort(403)

    if not report.document_path:
        abort(404)

    return send_from_directory("uploads", report.document_path)
