import os
import uuid
from pathlib import Path
from uuid import UUID

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile
from vercel.oidc.aio import get_vercel_oidc_token

from app.api.deps import AdminUser, DbSession
from app.core.config import settings
from app.modules.products import repository, service
from app.modules.products.importers import import_products
from app.modules.products.schemas import (
    CategoryCreate,
    CategoryOut,
    ImportResult,
    ProductCreate,
    ProductImageOut,
    ProductOut,
    ProductUpdate,
)

router = APIRouter()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(
    data: CategoryCreate,
    db: DbSession,
    _admin: AdminUser,
):
    slug = data.slug or service.slugify(data.name)

    if repository.get_category_by_slug(db, slug):
        raise HTTPException(
            status_code=400,
            detail="Slug already in use",
        )

    return service.create_category(db, data)

ALLOWED_IMPORT_EXTENSIONS = {".csv", ".json"}
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_IMPORT_SIZE_BYTES = 5 * 1024 * 1024

VERCEL_BLOB_API_URL = "https://vercel.com/api/blob"
VERCEL_BLOB_API_VERSION = "12"


async def upload_to_vercel_blob(
    pathname: str,
    content: bytes,
    *,
    content_type: str,
) -> str:

    oidc_token = await get_vercel_oidc_token()
    store_id = os.getenv("BLOB_STORE_ID")
    
    if not store_id:
        raise RuntimeError("BLOB_STORE_ID is not available")
        
    if store_id.startswith("store_"):
        store_id = store_id[len("store_"):]

    request_id = f"{store_id}:{uuid.uuid4().hex}"

    headers = {
        "authorization": f"Bearer {oidc_token}",
        "x-vercel-blob-store-id": store_id,
        "x-api-blob-request-id": request_id,
        "x-api-blob-request-attempt": "0",
        "x-api-version": VERCEL_BLOB_API_VERSION,
        "x-vercel-blob-access": "public",
        "x-content-type": content_type,
        "x-add-random-suffix": "0",
        "x-content-length": str(len(content)),
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.put(
                f"{VERCEL_BLOB_API_URL}/",
                params={"pathname": pathname},
                content=content,
                headers=headers,
            )
    except httpx.HTTPError as exc:
        raise RuntimeError("Could not connect to Vercel Blob") from exc

    if response.is_success:
        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError("Vercel Blob returned invalid JSON") from exc

        blob_url = data.get("url")

        if not blob_url:
            raise RuntimeError("Vercel Blob response did not contain a URL")

        return blob_url

    # Do not expose the OIDC token or raw response body to the client.
    raise RuntimeError(
        f"Vercel Blob upload failed with HTTP {response.status_code}"
    )


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(
    data: ProductCreate,
    db: DbSession,
    _admin: AdminUser,
):
    slug = data.slug or service.slugify(data.name)

    if repository.get_product_by_slug(db, slug):
        raise HTTPException(
            status_code=400,
            detail="Slug already in use",
        )

    return service.create_product(db, data)


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(
    product_id: UUID,
    data: ProductUpdate,
    db: DbSession,
    _admin: AdminUser,
):
    product = repository.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return service.update_product(db, product, data)


@router.delete("/products/{product_id}", response_model=ProductOut)
def archive_product(
    product_id: UUID,
    db: DbSession,
    _admin: AdminUser,
):
    product = repository.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return service.archive_product(db, product)


@router.post("/products/import", response_model=ImportResult)
async def import_products_endpoint(
    db: DbSession,
    _admin: AdminUser,
    file: UploadFile = File(...),
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_IMPORT_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .csv and .json files are accepted",
        )

    content = await file.read()

    if len(content) > MAX_IMPORT_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File too large (max 5MB)",
        )

    try:
        return import_products(
            db,
            file.filename,
            content,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/products/{product_id}/images",
    response_model=ProductImageOut,
    status_code=201,
)
async def upload_product_image(
    product_id: UUID,
    db: DbSession,
    _admin: AdminUser,
    file: UploadFile = File(...),
):
    # ----------------------------------------
    # 1. Verify product
    # ----------------------------------------
    product = repository.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # ----------------------------------------
    # 2. Validate image extension
    # ----------------------------------------
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type",
        )

    # ----------------------------------------
    # 3. Read and validate image size
    # ----------------------------------------
    content = await file.read()

    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail="Image too large",
        )

    # ----------------------------------------
    # 4. Generate unique Blob pathname
    # ----------------------------------------
    filename = f"{uuid.uuid4()}{extension}"
    pathname = f"products/{filename}"

    content_type = file.content_type or "application/octet-stream"

    # ----------------------------------------
    # 5. Upload to Vercel Blob
    # ----------------------------------------
    try:
        blob_url = await upload_to_vercel_blob(
            pathname,
            content,
            content_type=content_type,
        )
    except RuntimeError as exc:
        # Keep internal storage credentials/errors out
        # of the API response.
        print(f"Vercel Blob upload failed: {exc!r}")

        raise HTTPException(
            status_code=502,
            detail="Image storage upload failed",
        ) from exc

    # ----------------------------------------
    # 6. Save Blob URL in PostgreSQL
    # ----------------------------------------
    return service.add_image(
        db,
        product,
        url=blob_url,
        alt=product.name,
    )
