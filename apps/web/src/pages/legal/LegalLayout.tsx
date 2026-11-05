import type { ReactNode } from "react";

export interface LegalSection {
  title: string;
  content: ReactNode;
}

export function LegalLayout({ title, updated, sections }: { title: string; updated: string; sections: LegalSection[] }) {
  return (
    <article className="mx-auto max-w-3xl py-12 pb-24 sm:py-16">
      <p className="font-mono text-xs uppercase tracking-[0.18em] text-[var(--color-signal)]">FSOCIETY / INFORMATION</p>
      <h1 className="mt-4 font-display text-4xl leading-tight text-[var(--color-paper)] sm:text-5xl">{title}</h1>
      <p className="mt-3 text-sm text-[var(--color-steel)]">Last updated: {updated}</p>
      <div className="mt-10 space-y-9">
        {sections.map((section, index) => (
          <section key={section.title}>
            <h2 className="font-display text-xl text-[var(--color-paper)]">{String(index + 1).padStart(2, "0")} / {section.title}</h2>
            <div className="mt-3 space-y-3 text-sm leading-7 text-[var(--color-steel)]">{section.content}</div>
          </section>
        ))}
      </div>
    </article>
  );
}

export function LegalParagraph({ children }: { children: ReactNode }) {
  return <p>{children}</p>;
}
