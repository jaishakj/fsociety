from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.products.models import Category, Product, ProductImage, ProductStatus
from app.modules.products.service import slugify

CATEGORIES = ["summer-dresses", "party-dresses", "casual-dresses", "floral-dresses"]

PRODUCTS = [
    {
        "name": "Void Slip Dress",
        "category_slug": "party-dresses",
        "price": Decimal("2499.00"),
        "description": "A minimal black slip dress with a satin finish.",
        "images": ["https://images.example.com/void-slip-dress.jpg"],
    },
    {
        "name": "Ember Wrap Dress",
        "category_slug": "summer-dresses",
        "price": Decimal("1899.00"),
        "description": "Lightweight wrap dress in a warm ember red.",
        "images": ["https://images.example.com/ember-wrap-dress.jpg"],
    },
]


def seed() -> None:
    with SessionLocal() as db:
        category_by_slug = {}
        for slug in CATEGORIES:
            category = db.scalar(select(Category).where(Category.slug == slug))
            if not category:
                category = Category(name=slug.replace("-", " ").title(), slug=slug)
                db.add(category)
                db.flush()
            category_by_slug[slug] = category

        for item in PRODUCTS:
            slug = slugify(item["name"])
            existing = db.scalar(select(Product).where(Product.slug == slug))
            if existing:
                continue

            product = Product(
                name=item["name"],
                slug=slug,
                description=item["description"],
                price=item["price"],
                category_id=category_by_slug[item["category_slug"]].id,
                stock=25,
                status=ProductStatus.PUBLISHED,
            )
            for position, url in enumerate(item["images"]):
                product.images.append(ProductImage(url=url, position=position))
            db.add(product)

        db.commit()

    print("Seed complete.")


if __name__ == "__main__":
    seed()
