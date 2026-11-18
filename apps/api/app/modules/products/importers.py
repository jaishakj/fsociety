import csv
import io
import json
from decimal import Decimal, InvalidOperation

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.modules.products import repository, service
from app.modules.products.schemas import (
    ImportResult,
    ImportRowError,
    ProductCreate,
    ProductVariantWrite,
)

REQUIRED_FIELDS = {"name", "price", "category_slug"}


def _parse_csv(content: bytes) -> list[dict]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def _parse_json(content: bytes) -> list[dict]:
    data = json.loads(content.decode("utf-8"))
    if isinstance(data, dict):
        data = data.get("products", [])
    if not isinstance(data, list):
        raise TypeError('JSON import must be a list of products or {"products": [...]}')
    return data


def import_products(db: Session, filename: str, content: bytes) -> ImportResult:
    if filename.endswith(".csv"):
        rows = _parse_csv(content)
    elif filename.endswith(".json"):
        rows = _parse_json(content)
    else:
        raise ValueError("Only .csv and .json files are supported")

    created = 0
    skipped = 0
    errors: list[ImportRowError] = []

    for index, row in enumerate(rows, start=1):
        try:
            missing = REQUIRED_FIELDS - row.keys()
            if missing:
                raise ValueError(f"missing fields: {', '.join(sorted(missing))}")

            name = str(row["name"]).strip()
            if not name:
                raise ValueError("name is empty")

            try:
                price = Decimal(str(row["price"]))
            except InvalidOperation as exc:
                raise ValueError("invalid price") from exc
            if price <= 0:
                raise ValueError("price must be greater than 0")

            category_slug = str(row["category_slug"]).strip()
            category = repository.get_category_by_slug(db, category_slug)
            if not category:
                raise ValueError(f"unknown category_slug '{category_slug}'")

            slug = str(row.get("slug") or service.slugify(name))
            if repository.get_product_by_slug(db, slug):
                skipped += 1
                continue

            stock_raw = row.get("stock")
            try:
                stock = int(stock_raw) if stock_raw not in (None, "") else None
            except ValueError as exc:
                raise ValueError("invalid stock") from exc
            if stock is not None and stock < 0:
                raise ValueError("stock cannot be negative")

            status_raw = str(row.get("status") or "draft").strip().lower()
            variants_raw = row.get("variants", [])
            if isinstance(variants_raw, str):
                variants_raw = json.loads(variants_raw) if variants_raw.strip() else []
            if not isinstance(variants_raw, list):
                raise TypeError("variants must be a JSON array")
            variants = [ProductVariantWrite.model_validate(item) for item in variants_raw]

            image_urls = row.get("images", [])
            if image_urls is None:
                image_urls = []
            if isinstance(image_urls, str):
                image_urls = [u.strip() for u in image_urls.split("|") if u.strip()]

            if not variants and stock is None:
                stock = 0
            product_data = ProductCreate(
                name=name,
                slug=slug,
                description=row.get("description"),
                price=price,
                currency=str(row.get("currency") or "INR"),
                category_id=category.id,
                stock=stock,
                status=status_raw,
                variants=variants,
                images=image_urls,
            )
            with db.begin_nested():
                service.build_product(db, product_data)
                db.flush()
            created += 1

        except HTTPException as exc:
            errors.append(ImportRowError(row=index, error=str(exc.detail)))
        except ValidationError as exc:
            errors.append(ImportRowError(row=index, error=str(exc)))
        except Exception as exc:  # noqa: BLE001 - every row error is reported, not raised
            errors.append(ImportRowError(row=index, error=str(exc)))

    db.commit()
    return ImportResult(created=created, skipped=skipped, errors=errors)
