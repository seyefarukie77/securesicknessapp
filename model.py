from database import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)


class SicknessRecord(db.Model):
    __tablename__ = "sickness_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    full_day = db.Column(db.Boolean, default=True)
    reason = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    document_path = db.Column(db.String(255), nullable=True)

    employee = db.relationship("User", backref="sickness_records")

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": self.employee.name if self.employee else None,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date) if self.end_date else None,
            "full_day": self.full_day,
            "reason": self.reason,
            "status": self.status,
            "created_at": str(self.created_at),
            "document_path": self.document_path,
        }
