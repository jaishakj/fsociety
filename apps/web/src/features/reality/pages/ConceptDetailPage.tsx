import { Link, useParams } from "react-router-dom";

import { ConceptCard } from "../components/ConceptCard";
import { ConceptSections } from "../components/ConceptSections";
import { SourceList } from "../components/SourceList";
import { useConcept, useRelatedConcepts } from "../hooks/useReality";

const EVIDENCE_LABEL: Record<string, string> = {
  well_established: "Well established",
  supported: "Supported",
  mixed: "Mixed evidence",
  speculative: "Speculative",
  not_applicable: "Not applicable",
};

export default function ConceptDetailPage() {
  const { slug } = useParams();
  const { data: concept, isLoading } = useConcept(slug);
  const { data: related } = useRelatedConcepts(slug);

  if (isLoading || !concept) {
    return <p className="py-24 text-center text-[var(--color-steel)]">Loading&hellip;</p>;
  }

  return (
    <div className="pb-24">
      <section className="mt-6 rounded-[32px] border border-white/10 bg-[var(--color-panel)] px-6 py-16 md:px-16">
        <Link
          to={`/reality/topics/${concept.domain.slug}`}
          data-cursor
          className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]"
        >
          {concept.domain.name}
        </Link>
        <h1 className="font-display mt-4 max-w-2xl text-4xl text-[var(--color-paper)] md:text-5xl">
          {concept.title}
        </h1>
        <p className="mt-4 max-w-xl text-[var(--color-steel)]">{concept.summary}</p>

        <div className="font-mono mt-8 flex flex-wrap gap-3 text-[11px] uppercase tracking-wide">
          <span className="rounded-full border border-white/10 bg-black/30 px-3 py-1 text-[var(--color-signal)]">
            Evidence: {EVIDENCE_LABEL[concept.evidence_level] ?? concept.evidence_level}
          </span>
          <span className="rounded-full border border-white/10 bg-black/30 px-3 py-1 text-[var(--color-steel)]">
            {concept.difficulty}
          </span>
          <span className="rounded-full border border-white/10 bg-black/30 px-3 py-1 text-[var(--color-steel)]">
            {concept.estimated_reading_minutes} min read
          </span>
        </div>

        {concept.tags.length > 0 ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {concept.tags.map((tag) => (
              <span key={tag} className="font-mono text-xs text-[var(--color-steel)]">
                #{tag}
              </span>
            ))}
          </div>
        ) : null}
      </section>

      <div className="mt-10 grid grid-cols-1 gap-10 md:grid-cols-[2fr_1fr]">
        <div>
          <ConceptSections sections={concept.sections} />
        </div>

        <aside>
          <h2 className="font-display text-lg text-[var(--color-paper)]">Sources</h2>
          <SourceList sources={concept.sources} />
        </aside>
      </div>

      {related && related.length > 0 ? (
        <section className="mt-16">
          <h2 className="font-display text-2xl text-[var(--color-paper)]">Related concepts</h2>
          <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {related.map(({ relation_type, concept: relatedConcept }) => (
              <div key={relatedConcept.id}>
                <span className="font-mono text-[10px] uppercase tracking-wide text-[var(--color-steel)]">
                  {relation_type.replace(/_/g, " ")}
                </span>
                <div className="mt-1">
                  <ConceptCard concept={relatedConcept} />
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
