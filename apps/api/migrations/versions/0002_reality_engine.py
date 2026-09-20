"""human reality knowledge engine

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    difficulty = sa.Enum("beginner", "intermediate", "advanced", name="reality_difficulty")
    evidence_level = sa.Enum(
        "well_established", "supported", "mixed", "speculative", "not_applicable",
        name="reality_evidence_level",
    )
    content_status = sa.Enum(
        "draft", "research", "review", "approved", "published", "archived",
        name="reality_content_status",
    )
    source_type = sa.Enum(
        "research_paper", "book", "academic_book", "government_report",
        "institutional_report", "review", "news", "essay", "website",
        "documentary", "dataset",
        name="reality_source_type",
    )
    relation_type = sa.Enum(
        "related", "prerequisite", "contrasts_with", "extends", "example_of",
        "causes", "influences", "part_of",
        name="reality_relation_type",
    )

    op.create_table(
        "reality_domains",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reality_domains_slug", "reality_domains", ["slug"])

    op.create_table(
        "reality_sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("authors", JSONB, nullable=False, server_default="[]"),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("source_type", source_type, nullable=False),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("publisher", sa.String(255), nullable=True),
        sa.Column("doi", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reality_sources_url", "reality_sources", ["url"])

    op.create_table(
        "reality_concepts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("domain_id", sa.Uuid(), sa.ForeignKey("reality_domains.id"), nullable=False),
        sa.Column("difficulty", difficulty, nullable=False, server_default="beginner"),
        sa.Column("estimated_reading_minutes", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("content", JSONB, nullable=False, server_default="{}"),
        sa.Column("evidence_level", evidence_level, nullable=False),
        sa.Column("status", content_status, nullable=False, server_default="draft"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reality_concepts_slug", "reality_concepts", ["slug"])
    op.create_index("ix_reality_concepts_status", "reality_concepts", ["status"])
    op.create_index("ix_reality_concepts_domain_id", "reality_concepts", ["domain_id"])

    op.create_table(
        "reality_tags",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
    )

    op.create_table(
        "reality_concept_tags",
        sa.Column(
            "concept_id", sa.Uuid(),
            sa.ForeignKey("reality_concepts.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column(
            "tag_id", sa.Uuid(),
            sa.ForeignKey("reality_tags.id", ondelete="CASCADE"), primary_key=True,
        ),
    )

    op.create_table(
        "reality_concept_sources",
        sa.Column(
            "concept_id", sa.Uuid(),
            sa.ForeignKey("reality_concepts.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column(
            "source_id", sa.Uuid(),
            sa.ForeignKey("reality_sources.id", ondelete="CASCADE"), primary_key=True,
        ),
        sa.Column("section_type", sa.String(50), nullable=True),
    )

    op.create_table(
        "reality_concept_relations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "from_concept_id", sa.Uuid(),
            sa.ForeignKey("reality_concepts.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "to_concept_id", sa.Uuid(),
            sa.ForeignKey("reality_concepts.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("relation_type", relation_type, nullable=False),
        sa.UniqueConstraint(
            "from_concept_id", "to_concept_id", "relation_type",
            name="uq_reality_concept_relation",
        ),
    )
    op.create_index(
        "ix_reality_concept_relations_from", "reality_concept_relations", ["from_concept_id"]
    )
    op.create_index(
        "ix_reality_concept_relations_to", "reality_concept_relations", ["to_concept_id"]
    )


def downgrade() -> None:
    op.drop_table("reality_concept_relations")
    op.drop_table("reality_concept_sources")
    op.drop_table("reality_concept_tags")
    op.drop_table("reality_tags")
    op.drop_table("reality_concepts")
    op.drop_table("reality_sources")
    op.drop_table("reality_domains")

    for enum_name in (
        "reality_relation_type",
        "reality_source_type",
        "reality_content_status",
        "reality_evidence_level",
        "reality_difficulty",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
