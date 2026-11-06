from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def client_ip(request: Request) -> str:
    # Forwarded headers are attacker-controlled unless a trusted proxy is configured.
    return get_remote_address(request) or "unknown"


limiter = Limiter(key_func=client_ip, storage_uri=settings.rate_limit_storage_uri)
