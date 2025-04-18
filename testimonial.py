from app import db
from datetime import datetime

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=True) # Or title, project_type, etc.
    image_filename = db.Column(db.String(100), nullable=True) # Optional image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Testimonial {self.name}>' 