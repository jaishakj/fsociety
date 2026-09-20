import { useParams } from "react-router-dom";

import { ConceptCard } from "../components/ConceptCard";
import { useConcepts, useDomains } from "../hooks/useReality";

export default function TopicDetailPage() {
  const { slug } = useParams();
  const { data: domains } = useDomains();
  const { data: concepts, isLoading } = useConcepts({ domain: slug, page: 1 });

  const domain = domains?.find((d) => d.slug === slug);

  return (
    <div className="py-10 pb-24">
      <span className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">Topic</span>
      <h1 className="font-display mt-2 text-4xl text-[var(--color-paper)]">
        {domain?.name ?? "Loading\u2026"}
      </h1>
      {domain?.description ? <p className="mt-2 text-[var(--color-steel)]">{domain.description}</p> : null}

      <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          <p className="text-[var(--color-steel)]">Loading concepts&hellip;</p>
        ) : (concepts?.items ?? []).length === 0 ? (
          <p className="text-[var(--color-steel)]">No published concepts in this topic yet.</p>
        ) : (
          concepts!.items.map((concept) => <ConceptCard key={concept.id} concept={concept} />)
        )}
      </div>
    </div>
  );
}
