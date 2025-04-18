from app import db
from datetime import datetime

class JobOpening(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False) # e.g., Full-time, Part-time, Contract
    description = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text, nullable=True)
    qualifications = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    applications = db.relationship('JobApplication', backref='job_opening', lazy=True, 
                                 cascade="all, delete-orphan") # Delete applications if job is deleted

    def __repr__(self):
        return f'<JobOpening {self.title}>' 