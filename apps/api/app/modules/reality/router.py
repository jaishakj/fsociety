from fastapi import APIRouter

from app.modules.reality.concepts.router import router as concepts_router
from app.modules.reality.domains.router import router as domains_router
from app.modules.reality.sources.router import router as sources_router

reality_router = APIRouter()

reality_router.include_router(domains_router, prefix="/topics", tags=["reality:topics"])
reality_router.include_router(sources_router, prefix="/sources", tags=["reality:sources"])
reality_router.include_router(concepts_router, prefix="/concepts", tags=["reality:concepts"])
