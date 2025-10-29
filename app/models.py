from flask_login import UserMixin
from . import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

class DocumentSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    header = db.Column(db.String(255))  # store header text if this section is a header
    position = db.Column(db.Integer, nullable=False)  # ordering of sections
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class User(UserMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
