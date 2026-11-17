from fastapi import APIRouter, Request, Response, status

from app.api.deps import CurrentUser, DbSession
from app.core.rate_limit import limiter
from app.modules.commerce import repository
from app.modules.commerce.schemas import (
    CartMerchandiseQuoteIn,
    CartMerchandiseQuoteOut,
    CustomerCartOut,
    CustomerCartReplaceIn,
)
from app.modules.commerce.service import (
    build_merchandise_quote,
    get_customer_cart,
    replace_customer_cart,
)

router = APIRouter()


@router.post("/merchandise-quote", response_model=CartMerchandiseQuoteOut)
@limiter.limit("30/minute")
def quote_cart_merchandise(
    request: Request,
    data: CartMerchandiseQuoteIn,
    db: DbSession,
) -> CartMerchandiseQuoteOut:
    product_ids = {line.product_id for line in data.items}
    products = repository.list_published_products_by_ids(db, product_ids)
    return build_merchandise_quote(data, products)


@router.get("", response_model=CustomerCartOut)
def read_customer_cart(db: DbSession, current_user: CurrentUser) -> CustomerCartOut:
    return get_customer_cart(db, current_user.id)


@router.put("", response_model=CustomerCartOut)
@limiter.limit("30/minute")
def save_customer_cart(
    request: Request,
    data: CustomerCartReplaceIn,
    db: DbSession,
    current_user: CurrentUser,
) -> CustomerCartOut:
    return replace_customer_cart(db, current_user.id, data)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
def clear_customer_cart(
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    empty_cart = CustomerCartReplaceIn(items=[])
    replace_customer_cart(db, current_user.id, empty_cart)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
