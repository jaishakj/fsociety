import type { ConceptSource } from "../types/reality";

export function SourceList({ sources }: { sources: ConceptSource[] }) {
  if (sources.length === 0) {
    return (
      <p className="font-mono mt-4 text-xs text-[var(--color-steel)]">
        No sources attached to this concept yet.
      </p>
    );
  }

  return (
    <ul className="mt-4 space-y-3">
      {sources.map(({ source, section_type }) => (
        <li
          key={source.id}
          className="rounded-2xl border border-white/10 bg-black/20 p-4 text-sm text-[var(--color-steel)]"
        >
          <p className="text-[var(--color-paper)]">{source.title}</p>
          <p className="font-mono mt-1 text-[11px] uppercase tracking-wide">
            {source.authors.join(", ") || "Unknown author"}
            {source.publication_year ? ` \u00b7 ${source.publication_year}` : ""}
            {section_type ? ` \u00b7 supports: ${section_type}` : ""}
          </p>
          {source.url ? (
            <a
              href={source.url}
              target="_blank"
              rel="noreferrer"
              data-cursor
              className="mt-2 inline-block text-xs text-[var(--color-signal)] underline"
            >
              View source
            </a>
          ) : null}
        </li>
      ))}
    </ul>
  );
}
