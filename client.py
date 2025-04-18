from app import db
from datetime import datetime

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    logo_filename = db.Column(db.String(100), nullable=True) # Optional logo
    website_url = db.Column(db.String(255), nullable=True) # Optional website URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Client {self.name}>' 