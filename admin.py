from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, abort
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

# Define the relative paths within the static folder
TESTIMONIAL_UPLOAD_SUBDIR = 'uploads/testimonials'
CLIENT_UPLOAD_SUBDIR = 'uploads/clients'
PROJECT_IMAGE_UPLOAD_SUBDIR = 'uploads/project_images'
CERTIFICATE_UPLOAD_SUBDIR = 'uploads/certificates'
RESUME_UPLOAD_SUBDIR = 'uploads/resumes'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'pdf'}
ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}

bp = Blueprint('admin', __name__, url_prefix='/admin')

def get_upload_folder(subdir):
    return os.path.join(current_app.static_folder, subdir)

def allowed_file(filename, allowed_extensions=ALLOWED_IMAGE_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/projects/<int:id>/delete')
@admin_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    try:
        upload_folder = get_upload_folder(PROJECT_IMAGE_UPLOAD_SUBDIR)
        for image in project.images:
            try:
                image_path = os.path.join(upload_folder, image.filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
                else:
                    current_app.logger.warning(f"Project image file not found for deletion: {image_path}")
            except Exception as e:
                current_app.logger.error(f"Error deleting project image file {image.filename}: {e}")
                pass
        
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting project {id}: {e}", exc_info=True)
        flash(f'Error deleting project: {str(e)}', 'danger')
    return redirect(url_for('admin.dashboard'))

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    inquiries = ProjectInquiry.query.order_by(ProjectInquiry.created_at.desc()).limit(5).all()
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).limit(5).all()
    clients = Client.query.order_by(Client.name).all()
    certificates = Certificate.query.order_by(Certificate.name).limit(5).all()
    job_openings = JobOpening.query.filter_by(is_active=True).order_by(JobOpening.posted_date.desc()).limit(5).all()
    recent_applications = JobApplication.query.order_by(JobApplication.application_date.desc()).limit(10).all()

    testimonial_form = TestimonialForm(prefix='testimonial')
    client_form = ClientForm(prefix='client')
    certificate_form = CertificateForm(prefix='certificate')

    if testimonial_form.validate_on_submit() and testimonial_form.submit.data:
        try:
            testimonial = Testimonial(
                quote=testimonial_form.quote.data,
                name=testimonial_form.name.data,
                company=testimonial_form.company.data
            )
            
            if testimonial_form.image.data:
                file = testimonial_form.image.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_folder = get_upload_folder(TESTIMONIAL_UPLOAD_SUBDIR)
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    unique_filename = filename
                    while os.path.exists(os.path.join(upload_folder, unique_filename)):
                        unique_filename = f"{base}_{counter}{ext}"
                        counter += 1
                    os.makedirs(upload_folder, exist_ok=True)
                    file.save(os.path.join(upload_folder, unique_filename))
                    testimonial.image_filename = unique_filename
                else:
                    flash('Invalid testimonial image file type.', 'warning')

            db.session.add(testimonial)
            db.session.commit()
            flash('Testimonial added successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding testimonial: {e}", exc_info=True)
            flash(f'Error adding testimonial: {str(e)}', 'danger')

    if client_form.validate_on_submit() and client_form.submit.data:
        try:
            client = Client(
                name=client_form.name.data,
                website_url=client_form.website_url.data
            )

            if client_form.logo.data:
                file = client_form.logo.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_folder = get_upload_folder(CLIENT_UPLOAD_SUBDIR)
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    unique_filename = filename
                    while os.path.exists(os.path.join(upload_folder, unique_filename)):
                        unique_filename = f"{base}_{counter}{ext}"
                        counter += 1
                    os.makedirs(upload_folder, exist_ok=True)
                    file.save(os.path.join(upload_folder, unique_filename))
                    client.logo_filename = unique_filename
                else:
                    flash('Invalid client logo file type.', 'warning')
            
            db.session.add(client)
            db.session.commit()
            flash('Client added successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding client: {e}", exc_info=True)
            flash(f'Error adding client: {str(e)}', 'danger')

    if certificate_form.validate_on_submit() and certificate_form.submit.data:
        try:
            certificate = Certificate(
                name=certificate_form.name.data,
                issuing_body=certificate_form.issuing_body.data,
                issue_date=certificate_form.issue_date.data,
                expiry_date=certificate_form.expiry_date.data
            )

            if certificate_form.image.data:
                file = certificate_form.image.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_folder = get_upload_folder(CERTIFICATE_UPLOAD_SUBDIR)
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    unique_filename = filename
                    while os.path.exists(os.path.join(upload_folder, unique_filename)):
                        unique_filename = f"{base}_{counter}{ext}"
                        counter += 1
                    os.makedirs(upload_folder, exist_ok=True)
                    file.save(os.path.join(upload_folder, unique_filename))
                    certificate.image_filename = unique_filename
                else:
                    flash('Invalid certificate file type (Images or PDF only).', 'warning')
            
            db.session.add(certificate)
            db.session.commit()
            flash('Certificate added successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding certificate: {e}", exc_info=True)
            flash(f'Error adding certificate: {str(e)}', 'danger')

    return render_template('admin/dashboard.html', 
                         projects=projects, 
                         inquiries=inquiries, 
                         testimonials=testimonials,
                         clients=clients,
                         certificates=certificates,
                         job_openings=job_openings,
                         recent_applications=recent_applications,
                         testimonial_form=testimonial_form,
                         client_form=client_form,
                         certificate_form=certificate_form,
                         RESUME_UPLOAD_SUBDIR=RESUME_UPLOAD_SUBDIR)

@bp.route('/projects/new', methods=['GET', 'POST'])
@admin_required
def new_project():
    if request.method == 'POST':
        try:
            completion_date = None
            if request.form.get('completion_date'):
                completion_date = datetime.strptime(request.form['completion_date'], '%Y-%m-%d')

            project = Project(
                title=request.form['title'],
                description=request.form['description'],
                location=request.form['location'],
                project_type=request.form['project_type'],
                status=request.form['status'],
                budget=float(request.form['budget']),
                completion_date=completion_date,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(project)
            db.session.commit()
            
            if 'images[]' in request.files:
                files = request.files.getlist('images[]')
                upload_folder = get_upload_folder(PROJECT_IMAGE_UPLOAD_SUBDIR)
                os.makedirs(upload_folder, exist_ok=True)
                
                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        unique_filename = filename
                        while os.path.exists(os.path.join(upload_folder, unique_filename)):
                            unique_filename = f"{base}_{counter}{ext}"
                            counter += 1
                        
                        file.save(os.path.join(upload_folder, unique_filename))
                        image = ProjectImage(filename=unique_filename, project_id=project.id)
                        db.session.add(image)
                
                db.session.commit()
            
            flash('Project created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating project: {e}", exc_info=True)
            flash(f'Error creating project: {str(e)}', 'error')
            return render_template('admin/edit_project.html', project=None)
    
    return render_template('admin/edit_project.html', project=None)

@bp.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            project.title = request.form['title']
            project.description = request.form['description']
            project.location = request.form['location']
            project.project_type = request.form['project_type']
            project.status = request.form['status']
            project.budget = float(request.form['budget'])
            
            # Convert completion date string to datetime object
            completion_date = None
            if request.form.get('completion_date'):
                completion_date = datetime.strptime(request.form['completion_date'], '%Y-%m-%d')
            project.completion_date = completion_date
            
            if 'images[]' in request.files:
                files = request.files.getlist('images[]')
                upload_folder = get_upload_folder(PROJECT_IMAGE_UPLOAD_SUBDIR)
                os.makedirs(upload_folder, exist_ok=True)

                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        unique_filename = filename
                        while os.path.exists(os.path.join(upload_folder, unique_filename)):
                            unique_filename = f"{base}_{counter}{ext}"
                            counter += 1
                        
                        file.save(os.path.join(upload_folder, unique_filename))
                        image = ProjectImage(filename=unique_filename, project_id=project.id)
                        db.session.add(image)
            
            project.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating project {id}: {e}", exc_info=True)
            flash(f'Error updating project: {str(e)}', 'error')
            return render_template('admin/edit_project.html', project=project)
    
    return render_template('admin/edit_project.html', project=project)

@bp.route('/inquiries/<int:id>/update-status', methods=['POST'])
@admin_required
def update_inquiry_status(id):
    inquiry = ProjectInquiry.query.get_or_404(id)
    try:
        new_status = request.form.get('status')
        current_app.logger.info(f"Updating inquiry {id} status to: {new_status}")
        
        if new_status and new_status in ['pending', 'contacted', 'completed']:
            inquiry.status = new_status
            inquiry.updated_at = datetime.utcnow()
            db.session.add(inquiry)  # Explicitly add the object to the session
            db.session.commit()
            current_app.logger.info(f"Successfully updated inquiry {id} status to {new_status}")
            flash('Inquiry status updated successfully!', 'success')
        else:
            current_app.logger.warning(f"Invalid status provided for inquiry {id}: {new_status}")
            flash('Invalid status provided', 'warning')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating inquiry status {id}: {e}", exc_info=True)
        flash(f'Error updating inquiry status: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))

@bp.route('/testimonials/<int:id>/delete', methods=['GET', 'POST'])
@admin_required
def delete_testimonial(id):
    testimonial = Testimonial.query.get_or_404(id)
    try:
        # Delete the testimonial image if it exists
        if testimonial.image_filename:
            upload_folder = get_upload_folder(TESTIMONIAL_UPLOAD_SUBDIR)
            image_path = os.path.join(upload_folder, testimonial.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(testimonial)
        db.session.commit()
        flash('Testimonial deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting testimonial {id}: {e}", exc_info=True)
        flash(f'Error deleting testimonial: {str(e)}', 'danger')
    return redirect(url_for('admin.dashboard'))

@bp.route('/clients/<int:id>/delete', methods=['GET', 'POST'])
@admin_required
def delete_client(id):
    client = Client.query.get_or_404(id)
    try:
        # Delete the client logo if it exists
        if client.logo_filename:
            upload_folder = get_upload_folder(CLIENT_UPLOAD_SUBDIR)
            logo_path = os.path.join(upload_folder, client.logo_filename)
            if os.path.exists(logo_path):
                os.remove(logo_path)
        
        db.session.delete(client)
        db.session.commit()
        flash('Client deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting client {id}: {e}", exc_info=True)
        flash(f'Error deleting client: {str(e)}', 'danger')
    return redirect(url_for('admin.dashboard'))

@bp.route('/jobs/new', methods=['GET', 'POST'])
@admin_required
def add_job():
    form = JobOpeningForm()
    if form.validate_on_submit():
        try:
            job = JobOpening(
                title=form.title.data,
                description=form.description.data,
                responsibilities=form.responsibilities.data,
                qualifications=form.qualifications.data,
                location=form.location.data,
                job_type=form.job_type.data,
                posted_date=datetime.utcnow(),
                is_active=True
            )
            db.session.add(job)
            db.session.commit()
            flash('Job opening created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating job opening: {e}", exc_info=True)
            flash(f'Error creating job opening: {str(e)}', 'danger')
    return render_template('admin/edit_job.html', form=form, job=None)

@bp.route('/jobs')
@admin_required
def manage_jobs():
    jobs = JobOpening.query.order_by(JobOpening.posted_date.desc()).all()
    return render_template('admin/manage_jobs.html', jobs=jobs)

@bp.route('/jobs/<int:id>/applications')
@admin_required
def view_applications(id):
    job = JobOpening.query.get_or_404(id)
    applications = JobApplication.query.filter_by(job_opening_id=id).order_by(JobApplication.application_date.desc()).all()
    return render_template('admin/view_applications.html', job=job, applications=applications, RESUME_UPLOAD_SUBDIR=RESUME_UPLOAD_SUBDIR)

@bp.route('/jobs/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_job(id):
    job = JobOpening.query.get_or_404(id)
    form = JobOpeningForm(obj=job)
    
    if form.validate_on_submit():
        try:
            job.title = form.title.data
            job.description = form.description.data
            job.responsibilities = form.responsibilities.data
            job.qualifications = form.qualifications.data
            job.location = form.location.data
            job.job_type = form.job_type.data
            job.is_active = form.is_active.data
            
            db.session.commit()
            flash('Job opening updated successfully!', 'success')
            return redirect(url_for('admin.manage_jobs'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating job opening {id}: {e}", exc_info=True)
            flash(f'Error updating job opening: {str(e)}', 'danger')
    
    return render_template('admin/edit_job.html', form=form, job=job)

@bp.route('/jobs/<int:id>/delete', methods=['GET', 'POST'])
@admin_required
def delete_job(id):
    job = JobOpening.query.get_or_404(id)
    try:
        # Delete associated applications first
        JobApplication.query.filter_by(job_opening_id=id).delete()
        
        db.session.delete(job)
        db.session.commit()
        flash('Job opening deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting job opening {id}: {e}", exc_info=True)
        flash(f'Error deleting job opening: {str(e)}', 'danger')
    return redirect(url_for('admin.manage_jobs'))

@bp.route('/applications/<int:id>/reply', methods=['POST'])
@admin_required
def reply_to_application(id):
    application = JobApplication.query.get_or_404(id)
    try:
        reply_message = request.form.get('reply_message')
        if reply_message:
            application.admin_reply = reply_message
            application.reply_date = datetime.utcnow()
            application.status = 'replied'
            db.session.commit()
            
            # TODO: Send email notification to applicant
            flash('Reply sent successfully!', 'success')
        else:
            flash('Reply message cannot be empty', 'warning')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error replying to application {id}: {e}", exc_info=True)
        flash(f'Error sending reply: {str(e)}', 'danger')
    return redirect(url_for('admin.view_applications', id=application.job_opening_id))

@bp.route('/applications/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_application(id):
    application = JobApplication.query.get_or_404(id)
    try:
        # Delete the resume file if it exists
        if application.resume_filename:
            resume_path = os.path.join(current_app.static_folder, RESUME_UPLOAD_SUBDIR, application.resume_filename)
            if os.path.exists(resume_path):
                os.remove(resume_path)
        
        db.session.delete(application)
        db.session.commit()
        flash('Application deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting application.', 'danger')
    return redirect(url_for('admin.dashboard'))

@bp.route('/applications/<int:id>/update-status', methods=['POST'])
@admin_required
def update_application_status(id):
    application = JobApplication.query.get_or_404(id)
    try:
        new_status = request.form.get('status')
        if new_status:
            application.status = new_status
            application.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Application status updated successfully!', 'success')
        else:
            flash('No status provided', 'warning')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating application status {id}: {e}", exc_info=True)
        flash(f'Error updating application status: {str(e)}', 'danger')
    return redirect(url_for('admin.view_applications', id=application.job_opening_id))

@bp.route('/certificates/<int:id>/delete', methods=['GET', 'POST'])
@admin_required
def delete_certificate(id):
    certificate = Certificate.query.get_or_404(id)
    try:
        # Delete the certificate file if it exists
        if certificate.filename:
            certificate_path = os.path.join(current_app.static_folder, CERTIFICATE_UPLOAD_SUBDIR, certificate.filename)
            if os.path.exists(certificate_path):
                os.remove(certificate_path)
        
        db.session.delete(certificate)
        db.session.commit()
        flash('Certificate deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting certificate {id}: {e}", exc_info=True)
        flash(f'Error deleting certificate: {str(e)}', 'danger')
    return redirect(url_for('admin.dashboard'))

@bp.route('/inquiries/<int:id>/delete', methods=['POST'])
@admin_required
def delete_inquiry(id):
    inquiry = ProjectInquiry.query.get_or_404(id)
    try:
        db.session.delete(inquiry)
        db.session.commit()
        flash('Inquiry deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting inquiry {id}: {e}", exc_info=True)
        flash(f'Error deleting inquiry: {str(e)}', 'danger')
    return redirect(url_for('admin.dashboard'))