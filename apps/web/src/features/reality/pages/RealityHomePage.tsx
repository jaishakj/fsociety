import { Link } from "react-router-dom";

import { DepthStackHero } from "@/components/hero/DepthStackHero";
import { ConceptCard } from "../components/ConceptCard";
import { useConcepts, useDomains } from "../hooks/useReality";

export default function RealityHomePage() {
  const { data: domains } = useDomains();
  const { data: concepts } = useConcepts({ page: 1 });

  return (
    <div className="pb-24">
      <DepthStackHero
        eyebrow="Human Reality"
        title="KNOW REAL"
        subtitle="A source-backed map of how people and the world actually work. Concepts, not opinions, every claim traces back to a source, every evidence level stated plainly."
        imageUrl="/reality-hero.jpg"
        specs={[
          { label: "Topics", value: String(domains?.length ?? 9) },
          { label: "Concepts", value: `${concepts?.total ?? 140}+` },
        ]}
      />

      <section className="mt-10 flex flex-col items-start justify-between gap-4 rounded-3xl border border-white/10 bg-[var(--color-panel)] p-8 md:flex-row md:items-center">
        <div>
          <span className="font-mono text-xs uppercase tracking-wide text-[var(--color-signal)]">
            Start here
          </span>
          <h2 className="font-display mt-2 text-3xl text-[var(--color-paper)]">
            Browse by topic or search everything
          </h2>
        </div>
        <div className="flex flex-wrap gap-3">
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
