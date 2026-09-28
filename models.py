from extensions import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    joined_at = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime, nullable=False)

    tasks = db.relationship("Task", back_populates="user")
    recoveries = db.relationship("Recovery", back_populates="user")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    user = db.relationship("User", back_populates="tasks")


class Recovery(db.Model):
    __tablename__ = "recoveries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    sent_at = db.Column(db.Float, nullable=False)

    user = db.relationship("User", back_populates="recoveries")
