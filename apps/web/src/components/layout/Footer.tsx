export function Footer() {
  return (
    <footer className="mx-auto mt-24 max-w-6xl border-t border-white/10 px-6 py-10 font-mono text-xs text-[var(--color-steel)]">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <span>FSOCIETY / EST. 2026</span>
        <span>13.08&deg;N 80.27&deg;E &mdash; CHENNAI, IN</span>
        <span>&copy; {new Date().getFullYear()} FSOCIETY. ALL RIGHTS RESERVED.</span>
      </div>
    </footer>
  );
}
