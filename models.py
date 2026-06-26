from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

class Violation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20))
    violation_type = db.Column(db.String(100))
    location = db.Column(db.String(100))
    date = db.Column(db.String(20))
    fine_amount = db.Column(db.Integer)
    status = db.Column(db.String(10), default="Unpaid")
    image = db.Column(db.String(200))