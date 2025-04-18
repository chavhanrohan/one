from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField, FileAllowed

# Add other forms if they exist, or keep this as the only content if new file

class TestimonialForm(FlaskForm):
    quote = TextAreaField('Quote', 
                          validators=[DataRequired(), Length(min=10, max=500)], 
                          render_kw={"rows": 4})
    name = StringField('Client Name', validators=[DataRequired(), Length(max=100)])
    company = StringField('Company / Title', 
                          validators=[Optional(), Length(max=100)], 
                          description="Optional: Client's company or title")
    image = FileField('Client Image', 
                      validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')],
                      description="Optional: Upload a square image if possible (jpg, png, gif).")
    submit = SubmitField('Add Testimonial')

class ClientForm(FlaskForm):
    name = StringField('Client Name', validators=[DataRequired(), Length(max=150)])
    logo = FileField('Client Logo', 
                     validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'svg'], 'Images only (jpg, png, gif, svg)!')],
                     description="Optional: Upload client logo (prefer SVG or transparent PNG).")
    website_url = StringField('Website URL', 
                            validators=[Optional(), Length(max=255)],
                            description="Optional: Client's website address (e.g., https://example.com)")
    submit = SubmitField('Add Client')

class CertificateForm(FlaskForm):
    name = StringField('Certificate/Accreditation Name', validators=[DataRequired(), Length(max=200)])
    issuing_body = StringField('Issuing Body', validators=[Optional(), Length(max=200)])
    issue_date = DateField('Issue Date', validators=[Optional()], format='%Y-%m-%d')
    expiry_date = DateField('Expiry Date (if applicable)', validators=[Optional()], format='%Y-%m-%d')
    image = FileField('Certificate Image/Scan', 
                     validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf'], 'Images or PDF only!')],
                     description="Optional: Upload certificate scan (jpg, png, gif, pdf).")
    submit = SubmitField('Add Certificate')

JOB_TYPES = [('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Contract', 'Contract'), ('Internship', 'Internship')]

class JobOpeningForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=150)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    job_type = SelectField('Job Type', choices=JOB_TYPES, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()], render_kw={"rows": 5})
    responsibilities = TextAreaField('Responsibilities', validators=[Optional()], render_kw={"rows": 5})
    qualifications = TextAreaField('Qualifications', validators=[Optional()], render_kw={"rows": 5})
    is_active = BooleanField('Active (visible on website)', default=True)
    submit = SubmitField('Save Job Opening')

class JobApplicationForm(FlaskForm):
    applicant_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    applicant_email = StringField('Email Address', validators=[DataRequired(), Length(max=120)])
    applicant_phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    resume = FileField('Resume/CV', 
                       validators=[DataRequired(), FileAllowed(['pdf', 'doc', 'docx'], 'PDF or Word documents only!')],
                       description='Upload your resume (PDF, DOC, DOCX).')
    cover_letter = TextAreaField('Cover Letter (Optional)', validators=[Optional()], render_kw={"rows": 6})
    submit = SubmitField('Submit Application')

# Add ProjectForm if it doesn't exist elsewhere, or ensure it's imported if it does
# from flask_wtf import FlaskForm
# from wtforms import StringField, TextAreaField, SelectField, DecimalField, SubmitField
# from wtforms.validators import DataRequired, Length, Optional, NumberRange
# from flask_wtf.file import MultipleFileField, FileAllowed

# class ProjectForm(FlaskForm):
#     title = StringField('Project Title', validators=[DataRequired(), Length(max=120)])
#     description = TextAreaField('Description', validators=[DataRequired()])
#     project_type = SelectField('Project Type', choices=[
#         ('residential', 'Residential'),
#         ('commercial', 'Commercial'),
#         ('industrial', 'Industrial'),
#         ('infrastructure', 'Infrastructure')
#     ], validators=[DataRequired()])
#     status = SelectField('Status', choices=[
#         ('ongoing', 'Ongoing'),
#         ('completed', 'Completed'),
#         ('planned', 'Planned')
#     ], validators=[DataRequired()])
#     budget = DecimalField('Budget ($)', validators=[Optional(), NumberRange(min=0)], places=2)
#     location = StringField('Location', validators=[DataRequired(), Length(max=150)])
#     images = MultipleFileField('Project Images', validators=[
#         Optional(), 
#         FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
#     ])
#     submit = SubmitField('Save Project') 