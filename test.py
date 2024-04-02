from application import app 
from application import db_util


with app.app_context():
    # db_util.fix_item_entry(1000, category="Beverages") # modifying item entry
    # print(db_util.is_item_stock_low(1000)) # check if an item need stock in
    print("expense: ", db_util.get_expense())
    print("income: ", db_util.get_income())
