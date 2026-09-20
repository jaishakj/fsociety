import json
import re

import yaml
from sqlalchemy.orm import Session

from app.modules.reality.concepts import repository, service
from app.modules.reality.concepts.models import ContentStatus, Difficulty, EvidenceLevel
from app.modules.reality.concepts.schemas import ConceptCreate, ContentSection, ImportResult, ImportRowError
from app.modules.reality.domains import repository as domain_repository

REQUIRED_JSON_FIELDS = {"title", "domain", "evidence_level", "summary"}
REQUIRED_FRONTMATTER_FIELDS = {"title", "domain", "evidence_level", "summary"}
VALID_DIFFICULTIES = {d.value for d in Difficulty}
VALID_EVIDENCE_LEVELS = {e.value for e in EvidenceLevel}
VALID_STATUSES = {s.value for s in ContentStatus}


def _parse_markdown(content: bytes) -> dict:
    text = content.decode("utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("markdown file must start with a --- frontmatter block")

    frontmatter_raw, body = match.groups()
    frontmatter = yaml.safe_load(frontmatter_raw) or {}

    sections: list[dict] = []
    for block in re.split(r"^## ", body, flags=re.MULTILINE)[1:]:
        lines = block.strip().split("\n", 1)
        heading = lines[0].strip()
        body_text = lines[1].strip() if len(lines) > 1 else ""
        sections.append(
            {"type": service.slugify(heading), "title": heading, "content": body_text}
        )

    frontmatter["sections"] = sections
    return frontmatter


def _build_concept_create(item: dict) -> ConceptCreate:
    missing = REQUIRED_JSON_FIELDS - item.keys()
    if missing:
        raise ValueError(f"missing fields: {', '.join(sorted(missing))}")

    domain_slug = service.slugify(str(item["domain"]))
    difficulty = str(item.get("difficulty") or "beginner").strip().lower()
    if difficulty not in VALID_DIFFICULTIES:
        raise ValueError(f"invalid difficulty '{difficulty}'")

    evidence_level = str(item["evidence_level"]).strip().lower()
    if evidence_level not in VALID_EVIDENCE_LEVELS:
        raise ValueError(f"invalid evidence_level '{evidence_level}'")

    status = str(item.get("status") or "draft").strip().lower()
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status '{status}'")

    sections = [
        ContentSection(
            type=section.get("type", "section"),
            title=section.get("title", ""),
            content=section.get("content", ""),
        )
        for section in item.get("sections", [])
    ]

    return ConceptCreate(
        title=str(item["title"]),
        slug=item.get("slug"),
        summary=str(item["summary"]),
        domain_slug=domain_slug,
        difficulty=difficulty,
        evidence_level=evidence_level,
        estimated_reading_minutes=int(item.get("estimated_reading_minutes", 8)),
        status=status,
        sections=sections,
        tags=[str(t) for t in item.get("tags", [])],
    )


def import_concepts(db: Session, filename: str, content: bytes) -> ImportResult:
    if filename.endswith(".json"):
        raw = json.loads(content.decode("utf-8"))
        items = raw if isinstance(raw, list) else [raw]
    elif filename.endswith(".md"):
        items = [_parse_markdown(content)]
    else:
        raise ValueError("Only .json and .md files are supported")

    created = 0
    skipped = 0
    errors: list[ImportRowError] = []

    for index, item in enumerate(items, start=1):
        label = item.get("title") or item.get("slug") or f"item #{index}"
        try:
            data = _build_concept_create(item)

            if not domain_repository.get_domain_by_slug(db, data.domain_slug):
                raise ValueError(f"unknown domain '{data.domain_slug}', create it first")

            slug = data.slug or service.slugify(data.title)
            if repository.get_concept_by_slug(db, slug):
                skipped += 1
                continue

            service.create_concept(db, data)
            created += 1

        except Exception as exc:  # noqa: BLE001 - every item's error is reported, not raised
            errors.append(ImportRowError(item=str(label), error=str(exc)))

    return ImportResult(created=created, updated=0, skipped=skipped, errors=errors)
