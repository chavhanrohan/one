from app import db
from datetime import datetime

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    project_type = db.Column(db.String(50), nullable=False)  # residential, commercial, industrial
    budget = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='ongoing')  # ongoing, completed
    completion_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = db.relationship('ProjectImage', backref='project', lazy=True, 
                          cascade="all, delete-orphan")
    updates = db.relationship('ProjectUpdate', backref='project', lazy=True, 
                           cascade="all, delete-orphan")
    inquiries = db.relationship('ProjectInquiry', backref='project', lazy=True,
                            cascade="all, delete-orphan")

class ProjectImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    is_before = db.Column(db.Boolean, default=False)  # True for before images, False for after
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    progress_percentage = db.Column(db.Integer, default=0)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectInquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    status = db.Column(db.String(20), default='pending')  # pending, contacted, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 