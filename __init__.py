from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from datetime import datetime
import click
from flask.cli import with_appcontext
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from app.routes import main, auth, admin, projects, contact, chatbot
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(contact.bp)
    app.register_blueprint(chatbot.bp)

    # Add template context processor
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Add nl2br filter
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        if not s:
            return ""
        return s.replace('\n', '<br>')

    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print(f'Created uploads directory at {uploads_dir}')

    # Create database tables and default admin
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        from app.models.user import User
        default_admin = User.query.filter_by(username='rohan').first()
        if not default_admin:
            default_admin = User(
                username='rohan',
                email='rohan@example.com',
                is_admin=True
            )
            default_admin.set_password('Rohan@2004')
            db.session.add(default_admin)
            db.session.commit()
            print('Default admin user created successfully!')

    # Register CLI commands
    @app.cli.command("create-admin")
    @click.argument('username')
    @click.argument('email')
    @click.password_option()
    def create_admin(username, email, password):
        """Create an admin user"""
        from app.models.user import User
        user = User(username=username, email=email, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin user {username} created successfully!')

    return app 