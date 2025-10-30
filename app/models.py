from flask_login import UserMixin
from . import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

class User(UserMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)

    documents = db.relationship("Documents", back_populates="creator")
    AI_usage = db.relationship("AIInteractions", back_populates="chatlog")

class Documents(db.Model):
    
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    document_name = db.Column(db.String(255), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.String, default="")

    # new field to link to the user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship("User", back_populates="documents")

class AIInteractions(db.Model):

    __tablename__ = "AIinteractions"

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(10), nullable=False)  #ai or human
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    content = db.Column(db.String, nullable=False)

    chatlog = db.relationship("User", back_populates="AI_usage", foreign_keys=[user_id])