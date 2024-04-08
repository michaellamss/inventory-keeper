from application import app
from flask import render_template, url_for, redirect,flash, get_flashed_messages
from application.form import UserDataForm, AddItemForm, AddLedgerForm, AddTransactionForm
from application.models import IncomeExpenses, ItemModel, LedgerModel, TransactionModel
from application import db
from application import db_util
import json
from datetime import datetime

@app.before_request
def create_tables():
    # ItemModel.__table__.drop(db.engine) # table DROP
    db.create_all()

@app.route('/')
def index():
    current_year = datetime.now().year
    current_month = datetime.now().month

    ledgers = LedgerModel.query.filter(
        db.extract('year', LedgerModel.date) == current_year,
        db.extract('month', LedgerModel.date) == current_month
    ).all()

    ####################################################################################################
    #                                       best sellers chart                                         #
    ####################################################################################################

    item_changes = {}

    for ledger in ledgers:
        transactions = TransactionModel.query.filter_by(ledger_id = ledger.ledger_id).all()

        if transactions:
            for transaction in transactions:
                item_id = transaction.item_id
                item = ItemModel.query.filter_by(item_id = item_id).first()
                    
                if item_id not in item_changes:
                    item_changes[item_id] = {
                        'name': item.name,
                        'quantity_change': 0
                    }

                if transaction.transaction_type == "Stock-out":
                    item_changes[item_id]['quantity_change'] += transaction.units
    
    quantity_changes = []

    for item_id, item_data in item_changes.items():
        quantity_changes.append({
            'name': item_data['name'],
            'quantity_change': item_data['quantity_change']
        })

    sorted_quantity_changes = sorted(quantity_changes, key=lambda x: x['quantity_change'], reverse=True)

    ####################################################################################################
    #                                       revenue chart                                              #
    ####################################################################################################

    revenue = {}

    for ledger in ledgers:
        transactions = TransactionModel.query.filter_by(ledger_id = ledger.ledger_id).all()
        date = ledger.date.strftime("%d-%m-%y")

        if transactions:
            for transaction in transactions:
                item_id = transaction.item_id
                item = ItemModel.query.filter_by(item_id = item_id).first()

                if date not in revenue:
                    revenue[date] = {
                        'date': date,
                        'revenue': 0
                    }
                
                if transaction.transaction_type == "Stock-out":
                    revenue[date]['revenue'] +=  (item.unit_price * transaction.units)
        
    revenue_list = []

    for _, revenue in revenue.items():
        revenue_list.append({
            'date': revenue['date'],
            'revenue': revenue['revenue']
        })
    
    sorted_revenue_list = sorted(revenue_list, key=lambda x: x['date'])

    ####################################################################################################
    #                                       profiable chart                                            #
    ####################################################################################################

    profit = {}

    for ledger in ledgers:
        transactions = TransactionModel.query.filter_by(ledger_id = ledger.ledger_id).all()

        if transactions:
            for transaction in transactions:
                item_id = transaction.item_id
                item = ItemModel.query.filter_by(item_id = item_id).first()
                    
                if item_id not in profit:
                    profit[item_id] = {
                        'name': item.name,
                        'cost': 0,
                        'profit': 0
                    }

                if transaction.transaction_type == "Stock-out":
                    profit[item_id]['cost'] += (item.unit_cost  * transaction.units)
                    profit[item_id]['profit'] += ( (item.unit_price - item.unit_cost)  * transaction.units)
    
    profit_list = []

    for _, profit in profit.items():
        profit_list.append({
            'name': profit['name'],
            'cost': profit['cost'],
            'profit': profit['profit']
        })
    
    sorted_profit_list = sorted(profit_list, key=lambda x: x['profit'], reverse=True)

    print(sorted_profit_list)
    
    ####################################################################################################
    #                                       inventory chart                                            #
    ####################################################################################################

    inventories = ItemModel.query.all()

    inventory_list = []

    for inventory in inventories:
        print(f"inventory.name: {inventory.quantity}")
        inventory_list.append({
            'name': inventory.name,
            'quantity': inventory.quantity
        })


    return render_template('index.html', quantity_changes = json.dumps(sorted_quantity_changes), revenue = json.dumps(sorted_revenue_list), profit = json.dumps(sorted_profit_list[1]), inventory = json.dumps(inventory_list))


@app.route('/add', methods = ["POST", "GET"])
def add_expense():
    form = UserDataForm()
    if form.validate_on_submit():
        entry = IncomeExpenses(type=form.type.data, category=form.category.data, amount=form.amount.data)
        db.session.add(entry)
        db.session.commit()
        flash(f"{form.type.data} has been added to {form.type.data}s", "success")
        return redirect(url_for('index'))
    return render_template('add.html', title="Add expenses", form=form)

@app.route('/delete-post/<int:entry_id>')
def delete(entry_id):
    entry = IncomeExpenses.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted", "success")
    return redirect(url_for("index"))

@app.route('/dashboard')
def dashboard():
    income_vs_expense = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.type).group_by(IncomeExpenses.type).order_by(IncomeExpenses.type).all()

    category_comparison = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.category).group_by(IncomeExpenses.category).order_by(IncomeExpenses.category).all()

    dates = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.date).group_by(IncomeExpenses.date).order_by(IncomeExpenses.date).all()

    income_category = []
    for amounts, _ in category_comparison:
        income_category.append(amounts)

    income_expense = []
    for total_amount, _ in income_vs_expense:
        income_expense.append(total_amount)

    over_time_expenditure = []
    dates_label = []
    for amount, date in dates:
        dates_label.append(date.strftime("%m-%d-%y"))
        over_time_expenditure.append(amount)

    return render_template('dashboard.html',
                            income_vs_expense=json.dumps(income_expense),
                            income_category=json.dumps(income_category),
                            over_time_expenditure=json.dumps(over_time_expenditure),
                            dates_label =json.dumps(dates_label)
                        )
    
@app.route('/add_item', methods = ["POST", "GET"])
def add_item():
    form = AddItemForm()
    id = 100000 + len(ItemModel.query.all())
    
    if form.validate_on_submit():
        db_util.add_item(form)
        flash(f"{form.name.data} has been added", "success")
        return redirect(url_for('view_item'))

    return render_template('add_item.html', title="Add Item", form=form)

@app.route('/view_item')
def view_item():
    entries = db_util.get_all_items()
    return render_template('view_item.html', entries = entries)

@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    db_util.delete_item(item_id)
    flash("Item deleted", "success")
    return redirect(url_for("view_item"))

@app.route('/add_ledger', methods = ["POST", "GET"])
def add_ledger():
    form = AddLedgerForm()
    if form.validate_on_submit():
        db_util.add_ledger(form)
        flash(f"{form.title.data} has been added", "success")
        return redirect(url_for('view_ledger'))
    return render_template('add_ledger.html', title="Add Ledger", form=form)

@app.route('/view_ledger')
def view_ledger():
    entries = db_util.get_all_ledgers()
    return render_template('view_ledger.html', entries = entries)

@app.route('/delete_ledger/<int:ledger_id>')
def delete_ledger(ledger_id):
    db_util.delete_ledger(ledger_id)
    flash("Ledger deleted", "success")
    return redirect(url_for("view_ledger"))

@app.route('/view_ledger_transactions/<int:ledger_id>', methods = ["GET", "POST"])
def view_ledger_transactions(ledger_id):
    ledger = db_util.get_ledger(ledger_id)
    entries = db_util.get_transactions_by_ledger(ledger_id)
    reference = db_util.get_item_reference_dict()
    form = AddTransactionForm()
    if form.validate_on_submit():
        db_util.add_transaction(form, ledger_id)
        flash(f"New transaction record has been added", "success")
        return render_template('view_ledger_transactions.html', entries = db_util.get_transactions_by_ledger(ledger_id), ledger = ledger, reference=reference, form=AddTransactionForm())
    return render_template('view_ledger_transactions.html', entries = entries, ledger = ledger, reference=reference, form=form)

@app.route('/delete_transaction/<int:ledger_id>/<int:transaction_id>')
def delete_transaction(ledger_id, transaction_id):
    db_util.delete_transaction(transaction_id)
    return redirect(url_for("view_ledger_transactions", ledger_id=ledger_id))

@app.route('/apply_ledger/<int:ledger_id>')
def apply_ledger(ledger_id):
    db_util.apply_ledger(ledger_id)
    entries = db_util.get_all_ledgers()
    flash(f"Ledger applied", "success")
    return render_template('view_ledger.html', entries = entries)

@app.route('/view_transactions')
def view_transactions():
    entries = db_util.get_transactions_applied()
    reference = db_util.get_item_reference_dict()
    ledger_reference = db_util.get_ledger_reference_dict()
    return render_template('view_transactions.html', entries = entries, reference=reference, ledger_reference=ledger_reference)
    
