from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired
from application import app
from application import db_util

CATEGORIES = [
    ("Fruits and Vegetables", "Fruits and Vegetables"),
    ("Meat and Seafood", "Meat and Seafood"),
    ("Dairy and Eggs", "Dairy and Eggs"),
    ("Frozen Foods", "Frozen Foods"),
    ("Pantry Staples", "Pantry Staples"),
    ("Snacks and Sweets", "Snacks and Sweets"),
    ("Beverages", "Beverages"),
    ("Bakery and Bread", "Bakery and Bread"),
    ("Health and Wellness", "Health and Wellness"),
    ("International Foods", "International Foods"),
    ("Delicatessen", "Delicatessen"),
    ("Household Essentials", "Household Essentials"),
    ("Personal Care and Beauty", "Personal Care and Beauty"),
    ("Baby Products", "Baby Products"),
    ("Pet Supplies", "Pet Supplies"),
    ("Kitchen and Dining", "Kitchen and Dining"),
    ("Home and Electronics", "Home and Electronics"),
    ("Gardening and Outdoor", "Gardening and Outdoor"),
    ("Apparel and Accessories", "Apparel and Accessories"),
    ("Seasonal and Holiday", "Seasonal and Holiday")
]

TRANSACTION_TYPES = [
    ("Stock-in", "Stock-in"),
    ("Stock-out", "Stock-out"),
]

def make_item_categories():
    with app.app_context():
        items = db_util.get_all_items()
    categories = []
    for item in items:
        val = item.item_id
        display = "{} ({})".format(item.name,item.item_id)
        categories.append((val, display))
    return categories

class UserDataForm(FlaskForm):
    type = SelectField('Type', validators=[DataRequired()],
                                choices=[('income', 'income'),
                                        ('expense', 'expense')])
    category = SelectField("Category", validators=[DataRequired()],
                                            choices =[('rent', 'rent'),
                                            ('salary', 'salary'),
                                            ('investment', 'investment'),
                                            ('side_hustle', 'side_hustle')
                                            ]
                            )
    amount = IntegerField('Amount', validators = [DataRequired()])                                   
    submit = SubmitField('Generate Report')                            


class AddItemForm(FlaskForm):
    name = StringField('Product Name:', validators=[DataRequired()])
    description = StringField('Description:', validators=None)
    category = SelectField("Category:", validators=[DataRequired()], choices=CATEGORIES)    
    unit_cost = FloatField('Unit Cost:', validators=[DataRequired()])
    unit_price = FloatField('Unit Price:', validators=[DataRequired()])
    quantity = IntegerField('Initial Quantity:', validators = [DataRequired()])
    min_stock_level = IntegerField('Minimum Stock Level:', validators = [DataRequired()])
    supplier_information = StringField('Supplier Information:', validators=None)
    notes = StringField('Notes:', validators=None)
    submit = SubmitField('Confirm')        
    
class AddLedgerForm(FlaskForm):
    title = StringField('Ledger Title:', validators=[DataRequired()])
    date = StringField('Date: (YYYYDDMM e.g. 20240414)')
    submit = SubmitField('Create')

class AddTransactionForm(FlaskForm):
    item = SelectField("Item:", validators=[DataRequired()], choices=make_item_categories())    
    transaction_type = SelectField("Transaction Type:", validators=[DataRequired()], choices=TRANSACTION_TYPES)
    units = IntegerField('Units:', validators = [DataRequired()])
    signed_by = StringField('Signed By:', validators=None)
    notes = StringField('Notes:', validators=None)
    submit = SubmitField('Add')        
