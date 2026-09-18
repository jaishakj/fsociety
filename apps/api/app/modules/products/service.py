import re

from sqlalchemy.orm import Session

from app.modules.products.models import Category, Product, ProductImage, ProductStatus
from app.modules.products.schemas import CategoryCreate, ProductCreate, ProductUpdate


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def create_category(db: Session, data: CategoryCreate) -> Category:
    category = Category(
        name=data.name,
        slug=data.slug or slugify(data.name),
    )

    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(
        name=data.name,
        slug=data.slug or slugify(data.name),
        description=data.description,
        price=data.price,
        currency=data.currency,
        category_id=data.category_id,
        stock=data.stock,
        status=ProductStatus(data.status),
    )
    for position, url in enumerate(data.images):
        product.images.append(ProductImage(url=url, position=position))

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    updates = data.model_dump(exclude_unset=True)
    if updates.get("status") is not None:
        updates["status"] = ProductStatus(updates["status"])

    for field, value in updates.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def archive_product(db: Session, product: Product) -> Product:
    product.status = ProductStatus.ARCHIVED
    db.commit()
    db.refresh(product)
    return product


def add_image(db: Session, product: Product, url: str, alt: str | None = None) -> ProductImage:
    position = len(product.images)
    image = ProductImage(product_id=product.id, url=url, alt=alt, position=position)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image
