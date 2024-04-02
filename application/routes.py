from application import app
from flask import render_template, url_for, redirect,flash, get_flashed_messages
from application.form import UserDataForm, AddItemForm, AddLedgerForm, AddTransactionForm
from application.models import IncomeExpenses, ItemModel, LedgerModel, TransactionModel
from application import db
from application import db_util
import json

@app.before_request
def create_tables():
    # ItemModel.__table__.drop(db.engine) # table DROP
    db.create_all()

@app.route('/')
def index():
    entries = IncomeExpenses.query.order_by(IncomeExpenses.date.desc()).all()
    return render_template('index.html', entries = entries)


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
