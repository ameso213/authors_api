from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False) 
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contact = db.Column(db.String(50), nullable=False, unique=True)
    image = db.Column(db.String(225), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    biography = db.Column(db.Text(), nullable=True)
    user_type = db.Column(db.String(20), default='author')
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))  # Moved from _init_ to class definition
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    
    # Define relationship to books authored by the user
    books_authored = db.relationship('Book', backref='author', lazy=True)
    
    def __init__(self, first_name, last_name, email, contact, password, biography, user_type, company_id=None, image=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.contact = contact
        self.password_hash = password
        self.biography = biography
        self.user_type = user_type
        self.company_id = company_id
        self.image = image
        
    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"