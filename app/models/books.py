from app import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Integer, nullable=True)
    price_unit = db.Column(db.String(10), nullable=False, default='UGX')
    publication_date = db.Column(db.Date, nullable=False)  # Changed to Date type for publication date
    isbn = db.Column(db.String(30), nullable=False, unique=True)
    genre = db.Column(db.String(50), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    def _init_(self, title, description, price, price_unit, publication_date, isbn, genre, pages, user_id, company_id):
        super().__init__()  # Call superclass constructor
        self.title = title
        self.description = description
        self.price = price
        self.price_unit = price_unit
        self.publication_date = publication_date
        self.isbn = isbn
        self.genre = genre
        self.pages = pages
        self.user_id = user_id
        self.company_id = company_id

    def _repr_(self):
        return f'<Book {self.title}>'