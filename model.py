from database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class SicknessReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    full_day = db.Column(db.Boolean, default=True)
    reason = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    document_path = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "employee_name": self.employee_name,
            "department": self.department,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date) if self.end_date else None,
            "reason_category": self.reason_category,
            "notes": self.notes,
        }
    
