from ext import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(255))
    balance = db.Column(db.Float, default=5000)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    description = db.Column(db.Text)
    features = db.Column(db.Text)

    image = db.Column(db.String(255))

    # 🔥 FIX IS HERE
    gallery = db.relationship(
        "ProductGallery",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    box_items = db.relationship(
        "ProductBoxItem",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )


class ProductGallery(db.Model):
    __tablename__ = "product_gallery"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )
    image = db.Column(db.String(255))


class ProductBoxItem(db.Model):
    __tablename__ = "product_box_items"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )
    item = db.Column(db.String(255))

class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    
    # Relationship to easily pull all items in this cart
    items = db.relationship("CartItem", backref="cart", lazy=True, cascade="all, delete-orphan")


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    # Relationship to grab the product details directly from the cart item
    product = db.relationship("Product", lazy=True)