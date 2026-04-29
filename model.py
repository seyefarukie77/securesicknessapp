from database import db
from datetime import datetime


class SicknessRecord(db.Model):
    __tablename__ = "sickness_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    reason = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date) if self.end_date else None,
            "reason": self.reason,
            "created_at": str(self.created_at),
        }
