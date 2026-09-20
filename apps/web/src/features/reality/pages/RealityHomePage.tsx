import { Link } from "react-router-dom";

import { ConceptCard } from "../components/ConceptCard";
import { useConcepts, useDomains } from "../hooks/useReality";

export default function RealityHomePage() {
  const { data: domains } = useDomains();
  const { data: concepts } = useConcepts({ page: 1 });

  return (
    <div className="pb-24">
      <section className="mt-6 rounded-[32px] border border-white/10 bg-[var(--color-panel)] px-6 py-16 md:px-16 md:py-24">
        <span className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">
          Human Reality
        </span>
        <h1 className="font-display mt-4 max-w-2xl text-5xl text-[var(--color-paper)] md:text-6xl">
          A source-backed map of how people and the world actually work.
        </h1>
        <p className="mt-4 max-w-xl text-[var(--color-steel)]">
          Concepts, not opinions. Every claim here traces back to a source, every evidence level
          is stated plainly, and nothing is dressed up as more certain than it is.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            to="/reality/topics"
            data-cursor
            className="rounded-full bg-[var(--color-signal)] px-6 py-3 text-sm font-medium text-[var(--color-void)]"
          >
            Browse topics
          </Link>
          <Link
            to="/reality/concepts"
            data-cursor
            className="rounded-full border border-[var(--color-steel)] px-6 py-3 text-sm font-medium text-[var(--color-paper)]"
          >
            Explore all concepts
          </Link>
        </div>
      </section>

      {domains && domains.length > 0 ? (
        <section className="mt-16">
          <h2 className="font-display text-2xl text-[var(--color-paper)]">Topics</h2>
          <div className="mt-6 flex flex-wrap gap-3">
            {domains.map((domain) => (
              <Link
                key={domain.id}
                to={`/reality/topics/${domain.slug}`}
                data-cursor
                className="font-mono rounded-full border border-white/10 bg-[var(--color-panel)] px-4 py-2 text-xs uppercase tracking-wide text-[var(--color-steel)] hover:text-[var(--color-paper)]"
              >
                {domain.name}
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      <section className="mt-16">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="font-display text-2xl text-[var(--color-paper)]">Recent concepts</h2>
          <Link to="/reality/concepts" data-cursor className="font-mono text-xs uppercase text-[var(--color-steel)]">
            View all
          </Link>
        </div>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {(concepts?.items ?? []).map((concept) => (
            <ConceptCard key={concept.id} concept={concept} />
          ))}
        </div>
      </section>
    </div>
  );
}
