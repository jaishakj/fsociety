import re
import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.products import repository
from app.modules.products.models import (
    Category,
    Product,
    ProductImage,
    ProductStatus,
    ProductVariant,
)
from app.modules.products.schemas import (
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
    ProductVariantWrite,
)
from app.modules.products.sizing import sizes_for_category


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


def update_category(db: Session, category: Category, data: CategoryUpdate) -> Category:
    category.name = data.name.strip()
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> bool:
    db.delete(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return False
    return True


def _generated_variant_sku(product_slug: str, size: str) -> str:
    prefix = re.sub(r"[^A-Za-z0-9]", "", product_slug)[:80].upper() or "FSOC"
    return f"{prefix}-{size}-{uuid.uuid4().hex[:8].upper()}"


def _prepare_product_variants(
    db: Session,
    *,
    product_slug: str,
    category: Category,
    variants: list[ProductVariantWrite],
    existing_product: Product | None = None,
) -> list[ProductVariant]:
    allowed_sizes = sizes_for_category(category.slug, category.name)
    invalid_sizes = sorted({variant.size for variant in variants} - allowed_sizes)
    if invalid_sizes:
        if not allowed_sizes:
            raise HTTPException(
                status_code=422,
                detail="Footwear products do not use apparel size variants",
            )
        raise HTTPException(
            status_code=422,
            detail=f"Sizes are not valid for this product category: {', '.join(invalid_sizes)}",
        )

    existing_by_size = {
        variant.size: variant
        for variant in (existing_product.variants if existing_product else [])
    }
    requested_sizes = {variant.size for variant in variants}
    removed_with_stock = [
        variant.size
        for size, variant in existing_by_size.items()
        if size not in requested_sizes and variant.stock > 0
    ]
    if removed_with_stock:
        raise HTTPException(
            status_code=409,
            detail="Set removed variant stock to zero before removing its size",
        )

    desired: list[tuple[ProductVariantWrite, ProductVariant | None, str]] = []
    for item in variants:
        current = existing_by_size.get(item.size)
        sku = item.sku or (current.sku if current else None)
        if sku is None:
            sku = _generated_variant_sku(product_slug, item.size)
            while repository.product_variant_sku_exists(db, sku):
                sku = _generated_variant_sku(product_slug, item.size)
        desired.append((item, current, sku))

    desired_skus = [sku for _item, _current, sku in desired]
    if len(desired_skus) != len(set(desired_skus)):
        raise HTTPException(status_code=422, detail="Variant SKUs must be unique")
    if any(
        repository.product_variant_sku_exists(
            db,
            sku,
            exclude_product_id=existing_product.id if existing_product else None,
        )
        for _item, _current, sku in desired
    ):
        raise HTTPException(status_code=409, detail="A variant SKU is already in use")

    prepared: list[ProductVariant] = []
    for item, current, sku in desired:
        if current is None:
            prepared.append(ProductVariant(size=item.size, sku=sku, stock=item.stock))
        else:
            current.sku = sku
            current.stock = item.stock
            prepared.append(current)
    return prepared


def build_product(db: Session, data: ProductCreate) -> Product:
    category = repository.get_category_by_id(db, data.category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    variants = _prepare_product_variants(
        db,
        product_slug=data.slug or slugify(data.name),
        category=category,
        variants=data.variants,
    )
    product = Product(
        name=data.name,
        slug=data.slug or slugify(data.name),
        description=data.description,
        price=data.price,
        currency=data.currency,
        category_id=data.category_id,
        stock=sum(variant.stock for variant in variants) if variants else (data.stock or 0),
        status=ProductStatus(data.status),
        category=category,
        variants=variants,
    )
    for position, url in enumerate(data.images):
        product.images.append(ProductImage(url=url, position=position))

    db.add(product)
    return product


def create_product(db: Session, data: ProductCreate) -> Product:
    product = build_product(db, data)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    updates = data.model_dump(exclude_unset=True)
    variant_data = updates.pop("variants", None)
    if variant_data is not None:
        variant_data = [ProductVariantWrite.model_validate(item) for item in variant_data]
    category_id = updates.get("category_id", product.category_id)
    category = repository.get_category_by_id(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    if variant_data is not None:
        prepared_variants = _prepare_product_variants(
            db,
            product_slug=product.slug,
            category=category,
            variants=variant_data,
            existing_product=product,
        )
        if variant_data:
            product.variants = prepared_variants
            product.stock = sum(variant.stock for variant in prepared_variants)
            updates.pop("stock", None)
        else:
            product.variants.clear()
            product.stock = updates.pop("stock")
    elif product.variants:
        if updates.get("stock") is not None:
            raise HTTPException(
                status_code=422,
                detail="Update size-specific stock through the variants field",
            )
        allowed_sizes = sizes_for_category(category.slug, category.name)
        if any(variant.size not in allowed_sizes for variant in product.variants):
            raise HTTPException(
                status_code=422,
                detail="Update or remove variants before changing to this product category",
            )

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
