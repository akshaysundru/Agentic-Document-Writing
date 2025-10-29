from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import DevelopmentConfig
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login_page"  # type: ignore # Redirect here if login required

def create_app(config=DevelopmentConfig):
    flaskApp = Flask(__name__)
    flaskApp.config.from_object(config)

    # Initialize extensions with app
    db.init_app(flaskApp)
    migrate.init_app(flaskApp, db, render_as_batch=True)
    login_manager.init_app(flaskApp)

    # Register blueprints
    from .routes import main
    from .auth import auth
    flaskApp.register_blueprint(main)
    flaskApp.register_blueprint(auth)

    # Create DB if missing
    appdbPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    if not os.path.exists(appdbPath):
        with flaskApp.app_context():
            db.create_all()
            db.session.commit()

    # User loader for Flask-Login
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return flaskApp