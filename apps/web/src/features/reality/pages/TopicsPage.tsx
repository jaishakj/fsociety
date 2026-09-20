import { Link } from "react-router-dom";

import { useDomains } from "../hooks/useReality";

export default function TopicsPage() {
  const { data: domains, isLoading } = useDomains();

  return (
    <div className="py-10 pb-24">
      <h1 className="font-display text-4xl text-[var(--color-paper)]">Topics</h1>
      <p className="mt-2 text-[var(--color-steel)]">Browse the knowledge base by domain.</p>

      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          <p className="text-[var(--color-steel)]">Loading topics&hellip;</p>
        ) : (
          (domains ?? []).map((domain) => (
            <Link
              key={domain.id}
              to={`/reality/topics/${domain.slug}`}
              data-cursor
              className="rounded-3xl border border-white/10 bg-[var(--color-panel)] p-6 transition-colors hover:border-white/20"
            >
              <h2 className="font-display text-xl text-[var(--color-paper)]">{domain.name}</h2>
              {domain.description ? (
                <p className="mt-2 text-sm text-[var(--color-steel)]">{domain.description}</p>
              ) : null}
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
