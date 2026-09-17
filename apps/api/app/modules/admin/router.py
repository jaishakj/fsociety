import uuid
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile
from vercel.blob import AsyncBlobClient

from app.api.deps import AdminUser, DbSession
from app.core.config import settings
from app.modules.products import repository, service
from app.modules.products.importers import import_products
from app.modules.products.schemas import (
    ImportResult,
    ProductCreate,
    ProductImageOut,
    ProductOut,
    ProductUpdate,
)

router = APIRouter()

ALLOWED_IMPORT_EXTENSIONS = {".csv", ".json"}
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_IMPORT_SIZE_BYTES = 5 * 1024 * 1024


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, db: DbSession, _admin: AdminUser):
    slug = data.slug or service.slugify(data.name)
    if repository.get_product_by_slug(db, slug):
        raise HTTPException(status_code=400, detail="Slug already in use")
    return service.create_product(db, data)


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: UUID, data: ProductUpdate, db: DbSession, _admin: AdminUser):
    product = repository.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return service.update_product(db, product, data)


@router.delete("/products/{product_id}", response_model=ProductOut)
def archive_product(product_id: UUID, db: DbSession, _admin: AdminUser):
    product = repository.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return service.archive_product(db, product)


@router.post("/products/import", response_model=ImportResult)
async def import_products_endpoint(
    db: DbSession, _admin: AdminUser, file: UploadFile = File(...)
):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_IMPORT_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .csv and .json files are accepted")

    content = await file.read()
    if len(content) > MAX_IMPORT_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    try:
        return import_products(db, file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/products/{product_id}/images", response_model=ProductImageOut, status_code=201)
async def upload_product_image(
    product_id: UUID, db: DbSession, _admin: AdminUser, file: UploadFile = File(...)
):
    product = repository.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail="Image too large")

    filename = f"{uuid.uuid4()}{extension}"
    content_type = file.content_type or "application/octet-stream"
    
    try:
        async with AsyncBlobClient() as client:
            blob = await client.put(
                f"products/{filename}",
                content,
                access="public",
                content_type=content_type,
                add_random_suffix=False,
            )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Image storage upload failed",
        ) from exc
    
    return service.add_image(
        db,
        product,
        url=blob.url,
        alt=product.name,
    )
