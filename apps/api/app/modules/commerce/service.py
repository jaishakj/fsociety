from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.commerce import repository
from app.modules.commerce.models import CustomerCart, CustomerCartItem
from app.modules.commerce.schemas import (
    CartMerchandiseQuoteIn,
    CartMerchandiseQuoteLineOut,
    CartMerchandiseQuoteOut,
    CustomerCartItemOut,
    CustomerCartOut,
    CustomerCartReplaceIn,
)
from app.modules.products.models import Product
from app.modules.products.sizing import size_is_valid_for_category


def _product_size_is_valid(product: Product, size: str | None) -> bool:
    return size_is_valid_for_category(product.category.slug, product.category.name, size)


def _stock_for_size(product: Product, size: str | None) -> int:
    variants = getattr(product, "variants", [])
    if not variants:
        return product.stock
    variant = next((variant for variant in variants if variant.size == size), None)
    return variant.stock if variant is not None else 0


def _cart_item_out(item: CustomerCartItem, *, is_available: bool) -> CustomerCartItemOut:
    product = item.product
    return CustomerCartItemOut(
        id=item.id,
        product_id=product.id,
        name=product.name,
        slug=product.slug,
        category_slug=product.category.slug,
        category_name=product.category.name,
        quantity=item.quantity,
        size=item.size or None,
        unit_price=Decimal(product.price),
        currency=product.currency,
        image_url=product.images[0].url if product.images else None,
        is_available=is_available,
    )


def customer_cart_out(cart: CustomerCart | None) -> CustomerCartOut:
    if cart is None:
        return CustomerCartOut(cart_id=None, updated_at=None, items=[])

    quantities_by_product: dict[UUID, int] = defaultdict(int)
    quantities_by_line: dict[tuple[UUID, str], int] = defaultdict(int)
    for item in cart.items:
        quantities_by_product[item.product_id] += item.quantity
        quantities_by_line[(item.product_id, item.size)] += item.quantity

    items = [
        _cart_item_out(
            item,
            is_available=(
                item.product.status.value == "published"
                and quantities_by_product[item.product_id] <= item.product.stock
                and quantities_by_line[(item.product_id, item.size)]
                <= _stock_for_size(item.product, item.size or None)
            ),
        )
        for item in cart.items
    ]
    return CustomerCartOut(cart_id=cart.id, updated_at=cart.updated_at, items=items)


def get_customer_cart(db: Session, user_id: UUID) -> CustomerCartOut:
    return customer_cart_out(repository.get_customer_cart(db, user_id))


def replace_customer_cart(
    db: Session,
    user_id: UUID,
    data: CustomerCartReplaceIn,
) -> CustomerCartOut:
    quantities_by_product: dict[UUID, int] = defaultdict(int)
    quantities_by_line: dict[tuple[UUID, str], int] = defaultdict(int)
    for line in data.items:
        quantities_by_product[line.product_id] += line.quantity
        quantities_by_line[(line.product_id, line.size or "")] += line.quantity

    if any(quantity > 99 for quantity in quantities_by_line.values()):
        raise HTTPException(status_code=422, detail="A cart line cannot exceed 99 items")

    repository.lock_customer_row(db, user_id)
    products = repository.list_purchasable_products_by_ids(db, set(quantities_by_product))
    products_by_id = {product.id: product for product in products}
    if set(quantities_by_product) != set(products_by_id):
        raise HTTPException(status_code=409, detail="One or more products are unavailable")

    for product_id, quantity in quantities_by_product.items():
        product = products_by_id[product_id]
        if quantity > product.stock:
            raise HTTPException(status_code=409, detail="Requested quantity is unavailable")

    for line in data.items:
        if not _product_size_is_valid(products_by_id[line.product_id], line.size):
            raise HTTPException(status_code=422, detail="Select a valid size for each product")

    for (product_id, size), quantity in quantities_by_line.items():
        product = products_by_id[product_id]
        if quantity > _stock_for_size(product, size or None):
            raise HTTPException(status_code=409, detail="Requested size is unavailable")

    cart = repository.get_or_create_customer_cart(db, user_id)
    cart.items.clear()
    db.flush()
    for (product_id, size), quantity in quantities_by_line.items():
        cart.items.append(
            CustomerCartItem(
                product_id=product_id,
                size=size,
                quantity=quantity,
                product=products_by_id[product_id],
            )
        )
    cart.updated_at = datetime.now(UTC)
    db.flush()
    db.commit()
    return customer_cart_out(cart)


def build_merchandise_quote(
    request: CartMerchandiseQuoteIn,
    products: list[Product],
) -> CartMerchandiseQuoteOut:
    products_by_id = {product.id: product for product in products}
    requested_quantities: dict[UUID, int] = defaultdict(int)
    requested_by_line: dict[tuple[UUID, str], int] = defaultdict(int)
    for line in request.items:
        requested_quantities[line.product_id] += line.quantity
        requested_by_line[(line.product_id, line.size or "")] += line.quantity

    if set(requested_quantities) != set(products_by_id):
        raise HTTPException(status_code=409, detail="One or more products are unavailable")

    for line in request.items:
        if not _product_size_is_valid(products_by_id[line.product_id], line.size):
            raise HTTPException(status_code=422, detail="Select a valid size for each product")

    currencies = {product.currency for product in products_by_id.values()}
    if len(currencies) != 1:
        raise HTTPException(status_code=422, detail="Cart products must use the same currency")

    for product_id, quantity in requested_quantities.items():
        if quantity > products_by_id[product_id].stock:
            raise HTTPException(status_code=409, detail="Requested quantity is unavailable")

    for line in request.items:
        if not _product_size_is_valid(products_by_id[line.product_id], line.size):
            raise HTTPException(status_code=422, detail="Select a valid size for each product")

    for (product_id, size), quantity in requested_by_line.items():
        if quantity > _stock_for_size(products_by_id[product_id], size or None):
            raise HTTPException(status_code=409, detail="Requested size is unavailable")

    currency = next(iter(currencies))
    quote_lines: list[CartMerchandiseQuoteLineOut] = []
    subtotal = Decimal("0.00")
    for line in request.items:
        product = products_by_id[line.product_id]
        unit_price = Decimal(product.price)
        line_subtotal = unit_price * line.quantity
        subtotal += line_subtotal
        quote_lines.append(
            CartMerchandiseQuoteLineOut(
                product_id=product.id,
                name=product.name,
                quantity=line.quantity,
                size=line.size,
                unit_price=unit_price,
                line_subtotal=line_subtotal,
            )
        )

    return CartMerchandiseQuoteOut(
        currency=currency,
        items=quote_lines,
        merchandise_subtotal=subtotal,
    )
