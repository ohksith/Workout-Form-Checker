from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import datetime


db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    user_exercises = db.relationship('UserExercise', back_populates='user')
    weekly_workouts = db.relationship('WeeklyWorkout', back_populates='user')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Exercises(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    link = db.Column(db.String(200), unique=True, nullable=False)

    user_exercises = db.relationship('UserExercise', back_populates='exercise')


class UserExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=True)
    count = db.Column(db.Integer, nullable=True, default=0)
    last_performed_at = db.Column(db.DateTime, default=datetime.datetime.now)

    user = db.relationship('User', back_populates='user_exercises')
    exercise = db.relationship('Exercises', back_populates='user_exercises')


class WeeklyWorkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week_start = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())
    goal = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship('User', back_populates='weekly_workouts')