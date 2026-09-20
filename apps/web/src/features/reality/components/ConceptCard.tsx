import { Link } from "react-router-dom";

import type { ConceptSummary } from "../types/reality";

const EVIDENCE_LABEL: Record<string, string> = {
  well_established: "Well established",
  supported: "Supported",
  mixed: "Mixed evidence",
  speculative: "Speculative",
  not_applicable: "N/A",
};

export function ConceptCard({ concept }: { concept: ConceptSummary }) {
  return (
    <Link
      to={`/reality/concepts/${concept.slug}`}
      data-cursor
      className="block rounded-3xl border border-white/10 bg-[var(--color-panel)] p-6 transition-colors hover:border-white/20"
    >
      <div className="font-mono flex items-center gap-2 text-[10px] uppercase tracking-wide text-[var(--color-steel)]">
        <span>{concept.domain.name}</span>
        <span>&middot;</span>
        <span>{concept.difficulty}</span>
      </div>
      <h3 className="font-display mt-3 text-xl text-[var(--color-paper)]">{concept.title}</h3>
      <p className="mt-2 line-clamp-3 text-sm text-[var(--color-steel)]">{concept.summary}</p>
      <div className="font-mono mt-4 flex flex-wrap gap-2 text-[10px] uppercase tracking-wide">
        <span className="rounded-full border border-white/10 bg-black/30 px-2 py-1 text-[var(--color-signal)]">
          {EVIDENCE_LABEL[concept.evidence_level] ?? concept.evidence_level}
        </span>
        <span className="rounded-full border border-white/10 bg-black/30 px-2 py-1 text-[var(--color-steel)]">
          {concept.estimated_reading_minutes} min read
        </span>
      </div>
    </Link>
  );
}
