import re

FOOTWEAR_CATEGORY_PATTERN = re.compile(
    r"\b(foot\s*wears?|shoes?|sneakers?|trainers?|boots?|sandals?|slippers?|heels?|flats?)\b"
)
DRESS_CATEGORY_PATTERN = re.compile(r"\bdresses?\b")
APPAREL_SIZES = frozenset({"S", "M", "L", "XL", "XXL"})
DRESS_SIZES = APPAREL_SIZES | {"XS"}


def category_uses_apparel_sizes(slug: str, name: str) -> bool:
    category_text = f"{slug} {name}".replace("-", " ").replace("_", " ").lower()
    return not bool(FOOTWEAR_CATEGORY_PATTERN.search(category_text))


def sizes_for_category(slug: str, name: str) -> frozenset[str]:
    category_text = f"{slug} {name}".replace("-", " ").replace("_", " ").lower()
    if FOOTWEAR_CATEGORY_PATTERN.search(category_text):
        return frozenset()
    if DRESS_CATEGORY_PATTERN.search(category_text):
        return DRESS_SIZES
    return APPAREL_SIZES


def size_is_valid_for_category(slug: str, name: str, size: str | None) -> bool:
    allowed_sizes = sizes_for_category(slug, name)
    if not allowed_sizes:
        return size is None
    return size in allowed_sizes
