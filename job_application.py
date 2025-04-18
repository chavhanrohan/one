from app import db
from datetime import datetime

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_opening_id = db.Column(db.Integer, db.ForeignKey('job_opening.id'), nullable=False)
    applicant_name = db.Column(db.String(100), nullable=False)
    applicant_email = db.Column(db.String(120), nullable=False)
    applicant_phone = db.Column(db.String(20), nullable=True)
    resume_filename = db.Column(db.String(150), nullable=False) # Store filename of uploaded resume
    cover_letter = db.Column(db.Text, nullable=True)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default='Submitted') # e.g., Submitted, Reviewed, Interviewing, Rejected, Hired

    def __repr__(self):
        return f'<JobApplication {self.applicant_name} for {self.job_opening_id}>' 