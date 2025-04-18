from app import db
from datetime import datetime

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    issuing_body = db.Column(db.String(200), nullable=True)
    image_filename = db.Column(db.String(100), nullable=True) # Optional image/scan
    issue_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Certificate {self.name}>' 