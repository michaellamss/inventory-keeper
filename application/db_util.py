from application import app
from application import db
from application.models import ItemModel, LedgerModel, TransactionModel
from datetime import datetime


def get_item(item_id):
    try:
        item = ItemModel.query.get(item_id)
        return item
    except Exception as e:
        print(e)
        
def get_all_items():
    items = ItemModel.query.all()
    return items
    
def get_ledger(ledger_id):
    try:
        ledger = LedgerModel.query.get(ledger_id)
        return ledger
    except Exception as e:
        print(e)
        
def get_all_ledgers():
    ledgers = LedgerModel.query.all()
    return ledgers

def get_transaction(transaction_id):
    try:
        transaction = TransactionModel.query.get(transaction_id)
        return transaction
    except Exception as e:
        print(e)
        
def get_transactions_by_ledger(ledger_id):
    try:
        entries = TransactionModel.query.filter_by(ledger_id=ledger_id).all()    
        return entries
    except Exception as e:
        print(e)

def get_transactions_applied():
    try:
        entries = TransactionModel.query.filter_by(is_applied=True).all()    
        return entries
    except Exception as e:
        print(e)

def get_income():
    try:
        transactions = TransactionModel.query.filter_by(is_applied=True, transaction_type="Stock-out").all()    
        reference = get_item_reference_dict()
    except Exception as e:
        print(e)
    res = 0
    for transaction in transactions:
        res += reference[transaction.item_id][2] * transaction.units
    return res

def get_expense():
    try:
        transactions = TransactionModel.query.filter_by(is_applied=True, transaction_type="Stock-in").all()    
        reference = get_item_reference_dict()
    except Exception as e:
        print(e)
    res = 0
    for transaction in transactions:
        res += reference[transaction.item_id][1] * transaction.units
    return res



def add_item(form):
    id = 100000 + len(ItemModel.query.all())
    entry = ItemModel(
            item_id = id,
            name=form.name.data, 
            description=form.description.data, 
            category=form.category.data, 
            unit_cost=form.unit_cost.data, 
            unit_price=form.unit_price.data, 
            quantity=form.quantity.data, 
            min_stock_level=form.min_stock_level.data, 
            supplier_information=form.supplier_information.data,
            notes=form.notes.data
            )
    db.session.add(entry)
    db.session.commit()
    
def delete_item(item_id):
    item = get_item(item_id)
    db.session.delete(item)
    db.session.commit()

def fix_item_entry(item_id, name=None, description=None, category=None, unit_cost=None, unit_price=None, quantity=None, min_stock_level=None, supplier_information=None, notes=None) -> bool:
    item = get_item(item_id)
    if item:
        item.name = name if name else item.name 
        item.description = description if description else item.description
        item.category = category if category else item.category
        item.unit_cost = unit_cost if unit_cost else item.unit_cost
        item.unit_price = unit_price if unit_price else item.unit_price
        item.quantity = quantity if quantity else item.quantity
        item.min_stock_level = min_stock_level if min_stock_level else item.min_stock_level
        item.supplier_information = supplier_information if supplier_information else item.supplier_information
        item.notes = notes if notes else item.notes
        db.session.commit()  
    else:
        print("item_id={} not found")
        return False
    return True

def change_item_quantity(item_id, units, is_plus):
    item = get_item(item_id)
    if item:
        item.quantity = item.quantity + units if is_plus else item.quantity - units
    db.session.commit()  

def is_item_stock_low(item_id):
    item = get_item(item_id)
    return item.quantity < item.min_stock_level

def add_transction():
    pass
    
def add_ledger(form):
    id = 200000 + len(LedgerModel.query.all())
    date = datetime.strptime(form.date.data, "%Y%m%d") if is_valid_date(form.date.data) else datetime.now()
    try:
        entry = LedgerModel(ledger_id=id, date=date, title=form.title.data, is_applied=False)
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        print(e)
        return False
    return True
    
def delete_ledger(ledger_id):
    ledger = get_ledger(ledger_id)
    db.session.delete(ledger)
    db.session.commit()
    
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False
    
def get_item_reference_dict():
    res = dict()
    items = get_all_items()
    for item in items:
        res[item.item_id] = (item.name, item.unit_cost, item.unit_price)
    return res

def get_ledger_reference_dict():
    res = dict()
    ledgers = get_all_ledgers()
    for ledger in ledgers:
        res[ledger.ledger_id] = (ledger.title)
    return res
    
def add_transaction(form, ledger_id):
    id = 300000 + len(TransactionModel.query.all())
    entry = TransactionModel(
            transaction_id = id,
            ledger_id=ledger_id, 
            item_id=form.item.data, 
            transaction_type=form.transaction_type.data, 
            units=form.units.data, 
            signed_by=form.signed_by.data, 
            notes=form.notes.data, 
            is_applied=False
            )
    db.session.add(entry)
    db.session.commit()    
    
def delete_transaction(transaction_id):
    transaction = get_transaction(transaction_id)
    db.session.delete(transaction)
    db.session.commit()

def apply_ledger(ledger_id):
    ledger = get_ledger(ledger_id)
    transactions = get_transactions_by_ledger(ledger_id)
    ledger.is_applied = True
    for transaction in transactions:
        transaction.is_applied = True
        is_plus = True if transaction.transaction_type[-1] == 'i' else False
        change_item_quantity(transaction.item_id, transaction.units, is_plus)
    db.session.commit()

