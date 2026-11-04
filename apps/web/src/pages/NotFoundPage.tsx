import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center py-32 text-center">
      <h1 className="font-display text-4xl text-[var(--color-paper)]">404: Page not found</h1>
      <p className="mt-2 text-[var(--color-steel)]">The page you’re looking for doesn’t exist.</p>
      <Link
        to="/"
        data-cursor
        className="mt-8 rounded-full bg-[var(--color-signal)] px-6 py-3 text-sm font-medium text-[var(--color-void)]"
      >
        Back home
      </Link>
    </div>
  );
}
