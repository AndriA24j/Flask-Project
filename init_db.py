from ext import db, app
# Added Cart and CartItem here 
from models import User, Product, ProductGallery, ProductBoxItem, Cart, CartItem 

with app.app_context():
    db.drop_all()
    db.create_all()
    print('ბაზა წარმატებით შეიქმნა')