from ext import db
from datetime import datetime



class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    street = db.Column(db.String(150))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))

    balance = db.Column(db.Float, default=5000)

    orders = db.relationship(
    "Order",
    back_populates="user",
    lazy=True
)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    total_price = db.Column(
        db.Float,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    user = db.relationship(
        "User",
        back_populates="orders"
    )


    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy=True
    )

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )


    order = db.relationship(
        "Order",
        back_populates="items"
    )


    product = db.relationship(
        "Product"
    )



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