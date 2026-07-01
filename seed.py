from app import app
from ext import db
from models import Product, ProductGallery, ProductBoxItem
from products import products

with app.app_context():

    # 🔥 RESET DB
    db.drop_all()
    db.create_all()

    print("DB reset done")

    # 🔁 INSERT PRODUCTS
    for slug, data in products.items():

        # skip if exists (optional safety)
        if Product.query.filter_by(slug=slug).first():
            continue

        # 1. product
        product = Product(
            slug=slug,
            name=data["name"],
            price=data["price"],
            description=data["description"],
            features=data["features"],
            image=data["images"][0]
        )

        db.session.add(product)
        db.session.flush()  # gives product.id

        # 2. gallery
        for image in data["gallery"]:
            db.session.add(ProductGallery(
                product_id=product.id,
                image=image
            ))

        # 3. box items
        for item in data["box"]:
            db.session.add(ProductBoxItem(
                product_id=product.id,
                item=item
            ))

    db.session.commit()

    print("ყველა პროდუქტი წარმატებით დაემატა!")