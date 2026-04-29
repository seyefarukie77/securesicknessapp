import os
from uuid import uuid4
from werkzeug.utils import secure_filename


from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from database import db
from model import SicknessRecord

sickness_bp = Blueprint("sickness", __name__)


@sickness_bp.route("/", methods=["GET"])
def list_records():
    records = SicknessRecord.query.order_by(SicknessRecord.start_date.desc()).all()
    return render_template("records.html", records=records)


@sickness_bp.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        record = SicknessRecord(
            employee_id=int(request.form["employee_id"]),
            start_date=datetime.strptime(request.form["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(request.form["end_date"], "%Y-%m-%d").date(),
            reason=request.form["reason"],
        )
        db.session.add(record)
        db.session.commit()
        return redirect(url_for("sickness.list_records"))
    return render_template("submit.html")


@sickness_bp.route("/<int:record_id>/delete", methods=["POST"])
def delete_record(record_id):
    record = SicknessRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for("sickness.list_records"))
