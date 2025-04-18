from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.project import Project, ProjectImage, ProjectUpdate, ProjectInquiry
from app.models.testimonial import Testimonial
from app.models.client import Client
from app.models.certificate import Certificate
from app.models.job_opening import JobOpening
from app.models.job_application import JobApplication
from app.forms import TestimonialForm, ClientForm, CertificateForm, JobOpeningForm
from app import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    inquiries = ProjectInquiry.query.order_by(ProjectInquiry.created_at.desc()).limit(5).all()
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).limit(5).all()
    clients = Client.query.order_by(Client.name).limit(10).all()
    certificates = Certificate.query.order_by(Certificate.name).limit(5).all()
    job_openings = JobOpening.query.filter_by(is_active=True).order_by(JobOpening.posted_date.desc()).limit(5).all()
    recent_applications = JobApplication.query.order_by(JobApplication.application_date.desc()).limit(10).all()

    return render_template('admin/dashboard.html', 
                         projects=projects, 
                         inquiries=inquiries, 
                         testimonials=testimonials,
                         clients=clients,
                         certificates=certificates,
                         job_openings=job_openings,
                         recent_applications=recent_applications) 