from application import db
from datetime import datetime
import enum


class IncomeExpenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), default = 'income', nullable=False)
    category = db.Column(db.String(30), nullable=False, default='rent')
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Integer, nullable=False)
    
    
class ItemModel(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(30), nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    min_stock_level = db.Column(db.Integer, default=0)
    supplier_information = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.String(200), nullable=True)
    
class LedgerModel(db.Model):
    ledger_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 
    title = db.Column(db.String(100), nullable=False) 
    is_applied = db.Column(db.Boolean, default=False)
    
class TransactionModel(db.Model):
    transaction_id = db.Column(db.Integer, nullable=False, primary_key=True)
    ledger_id = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(30), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    signed_by =  db.Column(db.String(100), nullable=True)
    notes =  db.Column(db.String(200), nullable=True)
    is_applied = db.Column(db.Boolean, default=False)