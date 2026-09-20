import type { ContentSection } from "../types/reality";

export function ConceptSections({ sections }: { sections: ContentSection[] }) {
  if (sections.length === 0) {
    return null;
  }

  return (
    <div className="mt-10 space-y-8">
      {sections.map((section) => (
        <section key={section.type}>
          <h2 className="font-display text-xl text-[var(--color-paper)]">{section.title}</h2>
          <p className="mt-3 whitespace-pre-line leading-relaxed text-[var(--color-steel)]">
            {section.content}
          </p>
        </section>
      ))}
    </div>
  );
}
