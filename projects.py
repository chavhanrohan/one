from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.models.project import Project, ProjectImage, ProjectUpdate, ProjectInquiry
from app import db
from sqlalchemy import or_

bp = Blueprint('projects', __name__)

@bp.route('/projects')
def project_list():
    page = request.args.get('page', 1, type=int)
    query = Project.query

    # Apply filters
    project_type = request.args.get('type')
    if project_type:
        query = query.filter_by(project_type=project_type)

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    min_budget = request.args.get('min_budget', type=float)
    if min_budget:
        query = query.filter(Project.budget >= min_budget)

    max_budget = request.args.get('max_budget', type=float)
    if max_budget:
        query = query.filter(Project.budget <= max_budget)

    location = request.args.get('location')
    if location:
        query = query.filter(Project.location.ilike(f'%{location}%'))

    projects = query.order_by(Project.created_at.desc()).paginate(page=page, per_page=6)
    return render_template('projects/list.html', projects=projects)

@bp.route('/projects/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    
    # Get similar projects (same type or location)
    similar_projects = Project.query.filter(
        Project.id != id,
        or_(
            Project.project_type == project.project_type,
            Project.location == project.location
        )
    ).limit(3).all()
    
    return render_template('projects/detail.html', project=project, similar_projects=similar_projects)

@bp.route('/projects/<int:id>/inquiry', methods=['POST'])
def project_inquiry(id):
    project = Project.query.get_or_404(id)
    inquiry = ProjectInquiry(
        name=request.form.get('name'),
        email=request.form.get('email'),
        phone=request.form.get('phone'),
        message=request.form.get('message'),
        project_id=project.id
    )
    db.session.add(inquiry)
    db.session.commit()
    flash('Your inquiry has been submitted successfully! We will contact you soon.', 'success')
    return redirect(url_for('projects.project_detail', id=project.id))

@bp.route('/api/projects/search')
def search_projects():
    query = request.args.get('q', '')
    projects = Project.query.filter(
        or_(
            Project.title.ilike(f'%{query}%'),
            Project.description.ilike(f'%{query}%'),
            Project.location.ilike(f'%{query}%')
        )
    ).limit(5).all()
    
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'location': p.location,
        'type': p.project_type,
        'status': p.status
    } for p in projects])

@bp.route('/api/projects/filter')
def filter_projects():
    project_type = request.args.get('type')
    status = request.args.get('status')
    min_budget = request.args.get('min_budget', type=float)
    max_budget = request.args.get('max_budget', type=float)
    
    query = Project.query
    
    if project_type:
        query = query.filter_by(project_type=project_type)
    if status:
        query = query.filter_by(status=status)
    if min_budget is not None:
        query = query.filter(Project.budget >= min_budget)
    if max_budget is not None:
        query = query.filter(Project.budget <= max_budget)
    
    projects = query.all()
    
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'location': p.location,
        'type': p.project_type,
        'status': p.status,
        'budget': p.budget
    } for p in projects]) 