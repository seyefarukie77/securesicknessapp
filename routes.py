import os
from uuid import uuid4
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from database import db
from model import User, SicknessReport

sickness_bp = Blueprint("sickness", __name__)


@sickness_bp.route("/", methods=["GET"])
def list_records():
    records = SicknessRecord.query.order_by(SicknessRecord.start_date.desc()).all()
    return render_template("index.html", records=records)


@sickness_bp.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        record = SicknessRecord(
            employee_name=request.form["employee_name"],
            department=request.form["department"],
            start_date=datetime.strptime(request.form["start_date"], "%Y-%m-%d").date(),
            end_date=(
                datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
                if request.form.get("end_date")
                else None
            ),
            reason_category=request.form["reason_category"],
            notes=request.form.get("notes", ""),
        )
        db.session.add(record)
        db.session.commit()
        return redirect(url_for("sickness.list_records"))
    return render_template("submit.html")


@sickness_bp.route("/<int:record_id>/edit", methods=["GET", "POST"])
def edit_record(record_id):
    record = SicknessRecord.query.get_or_404(record_id)
    if request.method == "POST":
        record.employee_name = request.form["employee_name"]
        record.department = request.form["department"]
        record.start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        record.end_date = (
            datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
            if request.form.get("end_date")
            else None
        )
        record.reason_category = request.form["reason_category"]
        record.notes = request.form.get("notes", "")
        db.session.commit()
        return redirect(url_for("sickness.list_records"))
    return render_template("edit.html", record=record)


@sickness_bp.route("/<int:record_id>/delete", methods=["POST"])
def delete_record(record_id):
    record = SicknessRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for("sickness.list_records"))


@sickness_bp.route("/search", methods=["GET"])
def search():
    q = request.args.get("q", "").strip()
    dept = request.args.get("department", "").strip()
    query = SicknessRecord.query
    if q:
        query = query.filter(SicknessRecord.employee_name.ilike(f"%{q}%"))
    if dept:
        query = query.filter(SicknessRecord.department == dept)
    records = query.order_by(SicknessRecord.start_date.desc()).all()
    return render_template("index.html", records=records)
