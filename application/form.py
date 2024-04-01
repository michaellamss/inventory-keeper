from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired, NumberRange

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

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Description')