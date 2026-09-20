from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.reality.concepts.models import (
    Concept,
    ConceptRelation,
    ConceptSource,
    ConceptTag,
    ContentStatus,
    Difficulty,
    EvidenceLevel,
    RelationType,
    Tag,
)
from app.modules.reality.concepts.service import slugify
from app.modules.reality.domains.models import Domain
from app.modules.reality.sources.models import Source, SourceType

DOMAINS = [
    {"name": "Psychology", "slug": "psychology", "description": "How the mind actually works."},
    {"name": "Decision Making", "slug": "decision-making", "description": "How people choose, and why it often goes wrong."},
]

SOURCES = [
    {
        "title": "Thinking, Fast and Slow",
        "authors": ["Daniel Kahneman"],
        "source_type": SourceType.BOOK,
        "publication_year": 2011,
        "publisher": "Farrar, Straus and Giroux",
    },
    {
        "title": "A Theory of Cognitive Dissonance",
        "authors": ["Leon Festinger"],
        "source_type": SourceType.ACADEMIC_BOOK,
        "publication_year": 1957,
        "publisher": "Stanford University Press",
    },
]

CONCEPTS = [
    {
        "title": "Confirmation Bias",
        "domain": "psychology",
        "difficulty": Difficulty.BEGINNER,
        "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
        "estimated_reading_minutes": 6,
        "summary": "The tendency to search for, interpret, and recall information in ways that confirm what you already believe.",
        "sections": [
            {
                "type": "definition",
                "title": "What is it?",
                "content": "Confirmation bias is the tendency to favor information that supports existing beliefs while giving less weight to information that challenges them. It shows up in how people search for evidence, how they interpret ambiguous evidence, and what they remember afterward.",
            },
            {
                "type": "why-it-matters",
                "title": "Why it matters",
                "content": "It shapes everyday judgment calls, from how people evaluate news to how they assess their own past decisions, often without anyone noticing it happening.",
            },
            {
                "type": "limitations",
                "title": "Evidence and limitations",
                "content": "The effect is one of the most consistently replicated findings in cognitive psychology, though its size varies by context and by how emotionally invested someone is in the belief being tested.",
            },
        ],
        "tags": ["cognitive-bias", "reasoning"],
        "sources": [],
    },
    {
        "title": "Loss Aversion",
        "domain": "decision-making",
        "difficulty": Difficulty.BEGINNER,
        "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
        "estimated_reading_minutes": 7,
        "summary": "People tend to feel the pain of losing something roughly twice as strongly as the pleasure of gaining the same thing.",
        "sections": [
            {
                "type": "definition",
                "title": "What is it?",
                "content": "Loss aversion describes the asymmetry between how losses and equivalent gains are felt. Losing $50 tends to hurt more than gaining $50 feels good, even though the amounts are identical.",
            },
            {
                "type": "why-it-matters",
                "title": "Why it matters",
                "content": "It influences everything from investment decisions to negotiation tactics to why people hold on to underperforming choices longer than a purely rational calculation would suggest.",
            },
        ],
        "tags": ["cognitive-bias", "decision-making"],
        "sources": ["Thinking, Fast and Slow"],
    },
    {
        "title": "Anchoring Effect",
        "domain": "decision-making",
        "difficulty": Difficulty.BEGINNER,
        "evidence_level": EvidenceLevel.SUPPORTED,
        "estimated_reading_minutes": 5,
        "summary": "The first number or piece of information a person encounters disproportionately shapes their subsequent judgments, even when it is arbitrary.",
        "sections": [
            {
                "type": "definition",
                "title": "What is it?",
                "content": "Anchoring occurs when an initial reference point, even an irrelevant one, pulls later estimates toward it. Classic experiments show people's numeric guesses shift measurably based on an unrelated number they saw moments earlier.",
            },
        ],
        "tags": ["cognitive-bias", "decision-making"],
        "sources": ["Thinking, Fast and Slow"],
    },
    {
        "title": "Cognitive Dissonance",
        "domain": "psychology",
        "difficulty": Difficulty.INTERMEDIATE,
        "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
        "estimated_reading_minutes": 8,
        "summary": "The mental discomfort of holding two contradictory beliefs, or acting against a belief, and the ways people resolve that discomfort.",
        "sections": [
            {
                "type": "definition",
                "title": "What is it?",
                "content": "When actions and beliefs conflict, or two beliefs conflict with each other, the resulting discomfort tends to push people to change one of the beliefs, add a justifying belief, or downplay the conflict rather than sit with the inconsistency.",
            },
            {
                "type": "why-it-matters",
                "title": "Why it matters",
                "content": "It explains a wide range of otherwise puzzling behavior, including why people often become more committed to a choice after investing effort or money in it, regardless of how the choice turns out.",
            },
        ],
        "tags": ["psychology", "self-perception"],
        "sources": ["A Theory of Cognitive Dissonance"],
    },
    {
        "title": "Sunk Cost Fallacy",
        "domain": "decision-making",
        "difficulty": Difficulty.BEGINNER,
        "evidence_level": EvidenceLevel.SUPPORTED,
        "estimated_reading_minutes": 5,
        "summary": "The tendency to keep investing in something because of what has already been spent, rather than because of what it will return going forward.",
        "sections": [
            {
                "type": "definition",
                "title": "What is it?",
                "content": "A sunk cost is time, money, or effort that is already spent and cannot be recovered. The fallacy is letting that unrecoverable cost influence a decision that should only depend on future costs and benefits.",
            },
        ],
        "tags": ["decision-making", "cognitive-bias"],
        "sources": [],
    },
]

RELATIONS = [
    ("confirmation-bias", "cognitive-dissonance", RelationType.RELATED),
    ("loss-aversion", "anchoring-effect", RelationType.RELATED),
    ("sunk-cost-fallacy", "loss-aversion", RelationType.RELATED),
]


def seed() -> None:
    with SessionLocal() as db:
        domain_by_slug: dict[str, Domain] = {}
        for item in DOMAINS:
            domain = db.scalar(select(Domain).where(Domain.slug == item["slug"]))
            if not domain:
                domain = Domain(name=item["name"], slug=item["slug"], description=item["description"])
                db.add(domain)
                db.flush()
            domain_by_slug[item["slug"]] = domain

        source_by_title: dict[str, Source] = {}
        for item in SOURCES:
            source = db.scalar(select(Source).where(Source.title == item["title"]))
            if not source:
                source = Source(
                    title=item["title"],
                    authors=item["authors"],
                    source_type=item["source_type"],
                    publication_year=item["publication_year"],
                    publisher=item["publisher"],
                )
                db.add(source)
                db.flush()
            source_by_title[item["title"]] = source

        tag_by_name: dict[str, Tag] = {}

        def get_tag(name: str) -> Tag:
            if name not in tag_by_name:
                tag = db.scalar(select(Tag).where(Tag.name == name))
                if not tag:
                    tag = Tag(name=name)
                    db.add(tag)
                    db.flush()
                tag_by_name[name] = tag
            return tag_by_name[name]

        concept_by_slug: dict[str, Concept] = {}
        for item in CONCEPTS:
            slug = slugify(item["title"])
            existing = db.scalar(select(Concept).where(Concept.slug == slug))
            if existing:
                concept_by_slug[slug] = existing
                continue

            concept = Concept(
                slug=slug,
                title=item["title"],
                summary=item["summary"],
                domain_id=domain_by_slug[item["domain"]].id,
                difficulty=item["difficulty"],
                evidence_level=item["evidence_level"],
                estimated_reading_minutes=item["estimated_reading_minutes"],
                content={"sections": item["sections"]},
                status=ContentStatus.PUBLISHED,
            )
            for tag_name in item["tags"]:
                concept.tags.append(ConceptTag(tag=get_tag(tag_name)))
            for source_title in item["sources"]:
                concept.sources.append(ConceptSource(source_id=source_by_title[source_title].id))

            db.add(concept)
            db.flush()
            concept_by_slug[slug] = concept

        for from_slug, to_slug, relation_type in RELATIONS:
            from_concept = concept_by_slug.get(from_slug)
            to_concept = concept_by_slug.get(to_slug)
            if not from_concept or not to_concept:
                continue
            existing_relation = db.scalar(
                select(ConceptRelation).where(
                    ConceptRelation.from_concept_id == from_concept.id,
                    ConceptRelation.to_concept_id == to_concept.id,
                )
            )
            if not existing_relation:
                db.add(
                    ConceptRelation(
                        from_concept_id=from_concept.id,
                        to_concept_id=to_concept.id,
                        relation_type=relation_type,
                    )
                )

        db.commit()

    print("Reality seed complete.")


if __name__ == "__main__":
    seed()
