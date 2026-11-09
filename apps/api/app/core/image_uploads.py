from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

IMAGE_FORMATS = {
    ".jpg": ("JPEG", "image/jpeg", ".jpg"),
    ".jpeg": ("JPEG", "image/jpeg", ".jpg"),
    ".png": ("PNG", "image/png", ".png"),
    ".webp": ("WEBP", "image/webp", ".webp"),
}
MAX_IMAGE_PIXELS = 40_000_000
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


def validate_and_normalize_image(filename: str, content: bytes) -> tuple[bytes, str, str]:
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    expected = IMAGE_FORMATS.get(extension)
    if not expected or not content:
        raise ValueError("Only JPEG, PNG, and WebP images are accepted")

    expected_format, content_type, safe_extension = expected
    detected_format = (
        "JPEG" if content.startswith(b"\xff\xd8\xff")
        else "PNG" if content.startswith(b"\x89PNG\r\n\x1a\n")
        else "WEBP" if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP"
        else None
    )
    if detected_format != expected_format:
        raise ValueError("Image extension does not match its content")
    try:
        with Image.open(BytesIO(content)) as image:
            if image.format != expected_format:
                raise ValueError("Image extension does not match its content")
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ValueError("Image dimensions are too large")
            image.verify()

        with Image.open(BytesIO(content)) as image:
            image.load()
            normalized = ImageOps.exif_transpose(image)
            if expected_format == "JPEG" and normalized.mode not in {"RGB", "L"}:
                normalized = normalized.convert("RGB")
            output = BytesIO()
            save_options = {"optimize": True}
            if expected_format in {"JPEG", "WEBP"}:
                save_options["quality"] = 90
            normalized.save(output, format=expected_format, **save_options)
            return output.getvalue(), content_type, safe_extension
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Image could not be decoded safely") from exc
