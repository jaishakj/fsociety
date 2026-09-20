import { useState } from "react";

import { ConceptCard } from "../components/ConceptCard";
import { useConcepts, useDomains } from "../hooks/useReality";
import type { ConceptFilters } from "../types/reality";

const DIFFICULTIES = ["beginner", "intermediate", "advanced"];

export default function ConceptsPage() {
  const [filters, setFilters] = useState<ConceptFilters>({ page: 1 });
  const { data: domains } = useDomains();
  const { data: concepts, isLoading } = useConcepts(filters);

  return (
    <div className="py-10 pb-24">
      <h1 className="font-display text-4xl text-[var(--color-paper)]">Concepts</h1>
      <p className="font-mono mt-2 text-xs uppercase tracking-wide text-[var(--color-steel)]">
        {concepts ? `${concepts.total} concepts found` : "Loading"}
      </p>

      <div className="font-mono mt-6 flex flex-wrap items-center gap-2 rounded-2xl border border-white/10 bg-[var(--color-panel)] p-4 text-xs uppercase tracking-wide text-[var(--color-steel)]">
        <input
          type="text"
          placeholder="Search concepts..."
          data-cursor
          onChange={(e) => setFilters((prev) => ({ ...prev, q: e.target.value || undefined, page: 1 }))}
          className="mr-auto rounded-full border border-white/10 bg-transparent px-3 py-1 text-[var(--color-paper)] placeholder:text-[var(--color-steel)]"
        />
        <select
          data-cursor
          value={filters.domain ?? ""}
          onChange={(e) => setFilters((prev) => ({ ...prev, domain: e.target.value || undefined }))}
          className="rounded-full border border-white/10 bg-transparent px-3 py-1 text-[var(--color-paper)]"
        >
          <option value="">All topics</option>
          {(domains ?? []).map((domain) => (
            <option key={domain.id} value={domain.slug}>
              {domain.name}
            </option>
          ))}
        </select>
        <select
          data-cursor
          value={filters.difficulty ?? ""}
          onChange={(e) => setFilters((prev) => ({ ...prev, difficulty: e.target.value || undefined }))}
          className="rounded-full border border-white/10 bg-transparent px-3 py-1 text-[var(--color-paper)]"
        >
          <option value="">Any difficulty</option>
          {DIFFICULTIES.map((level) => (
            <option key={level} value={level}>
              {level}
            </option>
          ))}
        </select>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          <p className="text-[var(--color-steel)]">Loading&hellip;</p>
        ) : (concepts?.items ?? []).length === 0 ? (
          <p className="text-[var(--color-steel)]">No concepts match these filters.</p>
        ) : (
          concepts!.items.map((concept) => <ConceptCard key={concept.id} concept={concept} />)
        )}
      </div>
    </div>
  );
}
