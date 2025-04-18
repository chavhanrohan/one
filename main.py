from flask import Blueprint, render_template, flash, redirect, url_for
from app.models.project import Project
from app.models.testimonial import Testimonial # Import Testimonial model
from app.models.client import Client # Import Client model
from app.models.certificate import Certificate # Import Certificate model
from app.models.job_opening import JobOpening # Import JobOpening
from app.models.job_application import JobApplication # Import JobApplication
from app.forms import JobApplicationForm # Import JobApplicationForm
from app import db # Import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import current_app

# Define allowed file extensions and upload directories
ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}
RESUME_UPLOAD_SUBDIR = 'uploads/resumes'

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_upload_folder(subdir):
    return os.path.join(current_app.static_folder, subdir)

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    featured_projects = Project.query.order_by(Project.created_at.desc()).limit(6).all()
    # Fetch latest 3 testimonials for the homepage
    featured_testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).limit(3).all()
    # Fetch clients for the homepage
    clients = Client.query.order_by(Client.name).all()
    return render_template('index.html', 
                           featured_projects=featured_projects, 
                           featured_testimonials=featured_testimonials,
                           clients=clients) # Pass clients to index template

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/services')
def services():
    return render_template('services.html')

# Update the testimonials route to fetch data
@bp.route('/testimonials')
def testimonials():
    all_testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('testimonials.html', testimonials=all_testimonials)

# Update the clients route to fetch data
@bp.route('/clients')
def clients():
    all_clients = Client.query.order_by(Client.name).all()
    return render_template('clients.html', clients=all_clients)

# Update the certificates route to fetch data
@bp.route('/certificates')
def certificates():
    all_certificates = Certificate.query.order_by(Certificate.name).all() # Fetch all certificates
    return render_template('certificates.html', certificates=all_certificates)

@bp.route('/contact')
def contact():
    return render_template('contact.html')

# Update the career route to fetch active job openings
@bp.route('/career')
def career():
    job_openings = JobOpening.query.filter_by(is_active=True).order_by(JobOpening.posted_date.desc()).all()
    return render_template('career.html', job_openings=job_openings)

# Add route for job detail and application
@bp.route('/career/job/<int:id>', methods=['GET', 'POST'])
def job_detail(id):
    job = JobOpening.query.filter_by(id=id, is_active=True).first_or_404()
    form = JobApplicationForm()

    if form.validate_on_submit():
        try:
            application = JobApplication(
                job_opening_id=job.id,
                applicant_name=form.applicant_name.data,
                applicant_email=form.applicant_email.data,
                applicant_phone=form.applicant_phone.data,
                cover_letter=form.cover_letter.data
            )

            # Handle resume upload
            if form.resume.data:
                file = form.resume.data
                if allowed_file(file.filename, ALLOWED_RESUME_EXTENSIONS): # Use resume extensions
                    filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{job.id}_{file.filename}") # Unique name
                    upload_folder = get_upload_folder(RESUME_UPLOAD_SUBDIR)
                    os.makedirs(upload_folder, exist_ok=True)
                    file.save(os.path.join(upload_folder, filename))
                    application.resume_filename = filename
                else:
                    flash('Invalid resume file type (PDF or Word only).', 'warning')
                    return render_template('job_detail.html', job=job, form=form, RESUME_UPLOAD_SUBDIR=RESUME_UPLOAD_SUBDIR) # Re-render form on error
            else:
                 flash('Resume file is required.', 'danger')
                 return render_template('job_detail.html', job=job, form=form, RESUME_UPLOAD_SUBDIR=RESUME_UPLOAD_SUBDIR) # Re-render form

            db.session.add(application)
            db.session.commit()
            
            # Optional: Send notification email to admin/HR
            # ... (email sending logic here) ...

            flash('Your application has been submitted successfully!', 'success')
            return redirect(url_for('main.career'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error submitting application for job {id}: {e}", exc_info=True)
            flash(f'Error submitting application: {str(e)}', 'danger')

    return render_template('job_detail.html', job=job, form=form, RESUME_UPLOAD_SUBDIR=RESUME_UPLOAD_SUBDIR) 