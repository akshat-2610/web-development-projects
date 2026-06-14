from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    skills = db.Column(db.String(500), nullable=True)  # comma-separated list
    interests = db.Column(db.String(500), nullable=True)  # comma-separated list
    availability = db.Column(db.String(200), nullable=True)  # comma-separated list
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.Integer, default=1)
    badge = db.Column(db.String(50), default='Newcomer')
    
    # Relationships
    applications = db.relationship('Application', backref='volunteer', lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Environment, Education, Healthcare, Disaster Relief, Community
    date = db.Column(db.String(50), nullable=False)  # YYYY-MM-DD
    time = db.Column(db.String(50), nullable=False)  # e.g. "10:00 AM - 02:00 PM"
    location = db.Column(db.String(150), nullable=False)
    required_skills = db.Column(db.String(300), nullable=True)  # comma-separated list
    max_slots = db.Column(db.Integer, nullable=False, default=10)
    slots_filled = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), default='Active')  # Active, Archived
    
    # Relationships
    applications = db.relationship('Application', backref='opportunity', lazy=True, cascade="all, delete-orphan")

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteers.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=False)
    apply_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Denied, Completed
    hours_logged = db.Column(db.Float, default=0.0)
