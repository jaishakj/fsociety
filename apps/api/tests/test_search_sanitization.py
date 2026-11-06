from app.modules.products.repository import escape_like_query


def test_search_escapes_sql_like_wildcards_and_escape_character() -> None:
    assert escape_like_query(r"20%_off\sale") == r"20\%\_off\\sale"


def test_search_preserves_ordinary_text() -> None:
    assert escape_like_query("red dress") == "red dress"
