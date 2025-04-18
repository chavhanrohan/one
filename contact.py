from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_mail import Mail, Message
from app import db
from app.models.project import ProjectInquiry

bp = Blueprint('contact', __name__)
mail = Mail()

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Save inquiry to database
        inquiry = ProjectInquiry(
            name=name,
            email=email,
            phone=phone,
            message=f"Subject: {subject}\n\n{message}"
        )
        db.session.add(inquiry)
        db.session.commit()
        
        # Send email notification
        try:
            msg = Message(
                subject=f"New Contact Form Submission: {subject}",
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[current_app.config['MAIL_USERNAME']]
            )
            msg.body = f"""
            Name: {name}
            Email: {email}
            Phone: {phone}
            Subject: {subject}
            
            Message:
            {message}
            """
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")
        
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact.contact'))
    
    return render_template('contact.html')

@bp.route('/estimate', methods=['GET', 'POST'])
def estimate():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Save estimate request to database
            inquiry = ProjectInquiry(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone'),
                message=f"""
                Project Type: {data.get('project_type')}
                Square Footage: {data.get('square_footage')}
                Material Quality: {data.get('materials')}
                Timeline: {data.get('timeline')}
                Estimated Cost: {data.get('estimated_cost')}
                
                Description:
                {data.get('description')}
                """
            )
            db.session.add(inquiry)
            db.session.commit()
            
            # Send email notification
            try:
                msg = Message(
                    subject=f"New Project Estimate Request: {data.get('project_type')}",
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[current_app.config['MAIL_USERNAME']]
                )
                msg.body = f"""
                Name: {data.get('name')}
                Email: {data.get('email')}
                Phone: {data.get('phone')}
                Project Type: {data.get('project_type')}
                Square Footage: {data.get('square_footage')}
                Material Quality: {data.get('materials')}
                Timeline: {data.get('timeline')}
                Estimated Cost: {data.get('estimated_cost')}
                
                Description:
                {data.get('description')}
                """
                mail.send(msg)
            except Exception as e:
                current_app.logger.error(f"Failed to send email: {str(e)}")
            
            return jsonify({'success': True, 'message': 'Estimate request submitted successfully'})
        except Exception as e:
            current_app.logger.error(f"Error processing estimate request: {str(e)}")
            return jsonify({'success': False, 'message': 'Error processing request'}), 500
    
    return render_template('estimate.html') 