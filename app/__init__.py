from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import DevelopmentConfig
import os

#init
db = SQLAlchemy()
migrate = Migrate()

def create_app(config=DevelopmentConfig):
    flaskApp = Flask(__name__)
    flaskApp.config.from_object(config)
    db.init_app(flaskApp)  
    migrate.init_app(flaskApp, db, render_as_batch=True)

    from .routes import main
    flaskApp.register_blueprint(main)

    #app.db can get corrupted in git merges so leaving it in gitignore, this code will check if app.db exists and if not then create it
    appdbPath = os.path.join(os.path.abspath(os.path.dirname(__file__)) , 'app.db')
    if os.path.exists(appdbPath) == False:
         with flaskApp.app_context():
            db.create_all()
            db.session.commit()

    return flaskApp