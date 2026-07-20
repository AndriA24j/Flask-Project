import os
from ext import app, db
from models import User, Product, ProductGallery, ProductBoxItem, Cart, CartItem,OrderItem,Order
from flask import render_template, request, redirect, flash, url_for, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash

profile_bp = Blueprint("profile", __name__)

ADMIN_PASSWORD = "bermudi"



@app.route('/')
def home():
    return render_template('index.html')


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")

        if password and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_products"))
        else:
            flash("wrong password")

    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


def is_admin():
    return session.get("admin") is True


@app.route('/admin/products')
def admin_products():
    if not is_admin():
        return redirect(url_for("admin_login"))

    products = Product.query.all()
    return render_template("admin/products.html", products=products)


@app.route("/admin/products/create", methods=["GET", "POST"])
def create_product():
    if not is_admin():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = request.form.get("slug", "").strip()
        price_raw = request.form.get("price", "").strip()
        description = request.form.get("description", "").strip()
        features = request.form.get("features", "").strip()
        image = request.form.get("image", "").strip()

        # Basic required-field validation
        if not name or not slug or not price_raw:
            flash("სახელი, slug და ფასი სავალდებულოა")
            return redirect(url_for("create_product"))

        # Safely parse price instead of trusting raw form input
        try:
            price = float(price_raw)
            if price < 0:
                raise ValueError
        except ValueError:
            flash("ფასი უნდა იყოს სწორი რიცხვი")
            return redirect(url_for("create_product"))

        # Prevent duplicate slugs (avoids first_or_404 ambiguity later)
        if Product.query.filter_by(slug=slug).first():
            flash("ეს slug უკვე გამოყენებულია")
            return redirect(url_for("create_product"))

        new_product = Product(
            name=name,
            slug=slug,
            price=price,
            description=description,
            features=features,
            image=image
        )

        db.session.add(new_product)
        db.session.flush()  # get product.id BEFORE commit

        gallery_images = request.form.getlist("gallery")
        for img in gallery_images:
            if img and img.strip():
                db.session.add(ProductGallery(
                    image=img.strip(),
                    product_id=new_product.id
                ))

        db.session.commit()

        return redirect(url_for("admin_products"))

    return render_template("admin/create_product.html")


@app.route('/admin/products/delete/<int:id>')
def delete_product(id):
    if not is_admin():
        return redirect(url_for("admin_login"))

    product = Product.query.get_or_404(id)

    try:
        db.session.delete(product)
        db.session.commit()
        flash("პროდუქტი წაიშალა")
    except Exception:
        # Catches FK/integrity errors if related rows (gallery items,
        # cart items) aren't set up with cascading deletes in models.py
        db.session.rollback()
        flash("პროდუქტის წაშლა ვერ მოხერხდა — შეამოწმეთ დაკავშირებული ჩანაწერები")

    return redirect(url_for("admin_products"))


@app.route("/product/<slug>")
def product(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    return render_template("product.html", product=product)


@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("გთხოვთ გაიაროთ ავტორიზაცია კალათაში დასამატებლად")
        return redirect(url_for("login"))

    product = Product.query.get_or_404(product_id)

    user_cart = Cart.query.filter_by(user_id=user_id).first()
    if not user_cart:
        user_cart = Cart(user_id=user_id)
        db.session.add(user_cart)
        db.session.flush()

    cart_item = CartItem.query.filter_by(cart_id=user_cart.id, product_id=product.id).first()

    # Safely parse quantity instead of trusting raw form input
    try:
        quantity_to_add = int(request.form.get("quantity", 1))
        if quantity_to_add < 1:
            raise ValueError
    except (TypeError, ValueError):
        flash("რაოდენობა უნდა იყოს დადებითი მთელი რიცხვი")
        return redirect(request.referrer or url_for("techList"))

    if cart_item:
        cart_item.quantity += quantity_to_add
    else:
        new_item = CartItem(
            cart_id=user_cart.id,
            product_id=product.id,
            quantity=quantity_to_add
        )
        db.session.add(new_item)

    db.session.commit()
    flash(f"{product.name} დაემატა კალათაში!")

    return redirect(request.referrer or url_for("techList"))


@app.route('/cart')
def view_cart():
    user_id = session.get("user_id")
    if not user_id:
        flash("კალათის სანახავად გაიარეთ ავტორიზაცია")
        return redirect(url_for("login"))

    # 1. FETCH THE USER FROM THE DATABASE TO GET THE BALANCE
    # Replace 'User' with your actual User model name if it's different (e.g., Users)
    user = User.query.get(user_id) 
    user_balance = user.balance if user else 0

    user_cart = Cart.query.filter_by(user_id=user_id).first()

    cart_dict = {}
    total = 0

    if user_cart:
        for item in user_cart.items:
            if item.product:
                item_total = item.product.price * item.quantity
                total += item_total

                cart_dict[str(item.id)] = {
                    'name': item.product.name,
                    'price': item.product.price,
                    'qty': item.quantity
                }

    # 2. PASS 'balance=user_balance' INTO RENDER_TEMPLATE
    return render_template('cart.html', cart=cart_dict, total=total, balance=user_balance)


@app.route('/cart/remove/<int:id>')
def remove_from_cart(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user_cart = Cart.query.filter_by(user_id=user_id).first()
    if user_cart:
        item_to_delete = CartItem.query.filter_by(id=id, cart_id=user_cart.id).first()
        if item_to_delete:
            db.session.delete(item_to_delete)
            db.session.commit()
            flash("ნივთი წაიშალა კალათიდან")

    return redirect(url_for("view_cart"))


@app.route('/earphones')
def earphones():
    return render_template('earphones.html')


@app.route('/footer')
def footer():
    return render_template('footer.html')


@app.route('/headphones')
def headphones():
    return render_template('headphones.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("შეავსე ყველა ველი")
            return redirect(url_for("login"))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("მომხმარებელი ვერ მოიძებნა")
            return redirect(url_for("login"))

        if not check_password_hash(user.password, password):
            flash("პაროლი არასწორია")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["user_name"] = user.first_name
        session["email"] = user.email

        flash("წარმატებით შეხვედი")
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("გამოხვედი ანგარიშიდან")
    return redirect(url_for("home"))

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))


    user = User.query.get(session["user_id"])


    if request.method == "POST":

        # Update profile information

        if request.form.get("country"):
            user.country = request.form.get("country")

        if request.form.get("city"):
            user.city = request.form.get("city")

        if request.form.get("street"):
            user.street = request.form.get("street")

        if request.form.get("age"):
            user.age = int(request.form.get("age"))

        if request.form.get("phone"):
            user.phone = request.form.get("phone")


        db.session.commit()

        return redirect(url_for("profile"))



    return render_template(
        "profile.html",
        user=user,
        orders=user.orders
    )


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not first_name or not last_name or not email or not password or not confirm_password:
            flash("ყველა ველი უნდა შეავსო")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("პაროლები ერთმანეთს არ ემთხვევა")
            return redirect(url_for("register"))

        user_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if user_exists:
            flash("ეს email უკვე გამოყენებულია")
            return redirect(url_for("register"))

        if username_exists:
            flash("ეს მომხმარებლის სახელი უკვე გამოყენებულია")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("რეგისტრაცია წარმატებულია")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route('/speakers')
def speakers():
    return render_template('speakers.html')


@app.route("/techList")
def techList():

    query = Product.query


    # SEARCH

    search = request.args.get("search")

    if search:

        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )



    # MIN PRICE

    min_price = request.args.get("min_price")

    if min_price:

        query = query.filter(
            Product.price >= int(min_price)
        )



    # MAX PRICE

    max_price = request.args.get("max_price")

    if max_price:

        query = query.filter(
            Product.price <= int(max_price)
        )



    # SORT

    sort = request.args.get("sort")


    if sort == "price_low":

        query = query.order_by(
            Product.price.asc()
        )


    elif sort == "price_high":

        query = query.order_by(
            Product.price.desc()
        )


    elif sort == "name":

        query = query.order_by(
            Product.name.asc()
        )



    products = query.all()



    return render_template(
        "tech_List.html",
        products=products
    )



@app.route("/checkout_result", endpoint="checkout_result")
def checkout_result():
    result = session.get("last_order")

    if not result:
        return redirect(url_for("checkout"))

    return render_template(
        "checkout_result.html",
        success=result["success"],
        total=result.get("total"),
        balance=result.get("balance"),
        message=result.get("message")
    )


@app.route("/checkout", methods=["GET", "POST"], endpoint="checkout")
def checkout():
    user_id = session.get("user_id")

    print("USER ID FROM SESSION:", user_id)

    # User is not logged in
    if not user_id:
        return redirect(url_for("login"))

    # Get user safely
    user = User.query.get(user_id)

    print("USER FROM DATABASE:", user)

    if not user:
        return "User does not exist. Session has invalid user_id.", 500

    # Get user's cart
    user_cart = Cart.query.filter_by(user_id=user_id).first()

    print("USER CART:", user_cart)

    if not user_cart or not user_cart.items:
        flash("Your cart is empty.")
        return redirect(url_for("view_cart"))

    cart = {}
    total = 0

    # Build cart data
    for item in user_cart.items:
        if item.product:
            cart[item.id] = {
                "name": item.product.name,
                "price": item.product.price,
                "qty": item.quantity
            }

            total += item.product.price * item.quantity

    print("CART:", cart)
    print("TOTAL:", total)

    # When user clicks Complete Purchase
    if request.method == "POST":

        if user.balance < total:
            session["last_order"] = {
                "success": False,
                "message": "Insufficient balance."
            }

            return redirect(url_for("checkout_result"))

        # Create order
        order = Order(
            user_id=user.id,
            total_price=total
        )

        db.session.add(order)
        db.session.flush()

        # Add order items
        for item in user_cart.items:
            if item.product:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price
                )

                db.session.add(order_item)

        # Remove money
        user.balance -= total

        # Clear cart
        CartItem.query.filter_by(cart_id=user_cart.id).delete()

        db.session.commit()

        session["last_order"] = {
            "success": True,
            "total": total,
            "balance": user.balance
        }

        return redirect(url_for("checkout_result"))

    # Show checkout page
    return render_template(
        "checkout.html",
        cart=cart,
        total=total,
        balance=user.balance
    )