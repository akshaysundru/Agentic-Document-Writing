from flask_login import UserMixin
from . import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

class User(UserMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)

class Documents(db.Model):
    
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    document_name = db.Column(db.String(255), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.String, default="")
