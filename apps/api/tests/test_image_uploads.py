from io import BytesIO

import pytest
from PIL import Image

from app.core.image_uploads import validate_and_normalize_image


def png_bytes() -> bytes:
    image = Image.new("RGB", (2, 2), color=(255, 0, 0))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_png_is_verified_and_normalized() -> None:
    content, content_type, extension = validate_and_normalize_image("item.png", png_bytes())
    assert content_type == "image/png"
    assert extension == ".png"
    assert content.startswith(b"\x89PNG\r\n\x1a\n")


def test_rejects_svg_and_mismatched_extension() -> None:
    with pytest.raises(ValueError):
        validate_and_normalize_image("item.svg", b"<svg></svg>")
    with pytest.raises(ValueError, match="malformed or contains trailing"):
        validate_and_normalize_image("item.png", png_bytes() + b"<script>alert(1)</script>")


def test_rejects_extension_that_does_not_match_image_format() -> None:
    with pytest.raises(ValueError, match="extension does not match"):
        validate_and_normalize_image("item.jpg", png_bytes())
