from application import db
from datetime import datetime
import enum


class IncomeExpenses(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), default = 'income', nullable=False)
    category = db.Column(db.String(30), nullable=False, default='rent')
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Integer, nullable=False)

# Product model
class Product(db.Model):

    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    stock_quantity = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'