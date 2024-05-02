from app import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    origin = db.Column(db.String(100))
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    def _init_(self, name, origin, description, user_id):
        super().__init__()  # Call superclass constructor
        self.name = name
        self.origin = origin
        self.description = description
        self.user_id = user_id

    def _repr_(self):
        return f'<Company {self.name}>'