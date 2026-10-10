import { Instagram } from "lucide-react";
import { Link } from "react-router-dom";

export function Footer() {
  return (
    <footer className="mx-auto mt-24 max-w-6xl border-t border-white/10 px-6 py-12 text-sm text-[var(--color-steel)]">
      <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
        <div className="col-span-2 md:col-span-1">
          <span className="font-display text-lg text-[var(--color-paper)]">FSOCIETY</span>
          <p className="mt-3 text-xs">Dresses built for the person who refuses to blend in.</p>
          <a
            href="https://instagram.com"
            data-cursor
            aria-label="Instagram"
            className="mt-4 inline-flex rounded-full border border-white/10 p-2 hover:text-[var(--color-paper)]"
          >
            <Instagram size={16} />
          </a>
        </div>

        <div>
          <span className="font-mono text-xs uppercase tracking-wide text-[var(--color-paper)]">Shop</span>
          <ul className="mt-4 space-y-2 text-xs">
            <li>
              <Link to="/shop" data-cursor className="hover:text-[var(--color-paper)]">
                All products
              </Link>
            </li>
            <li>
              <Link to="/wishlist" data-cursor className="hover:text-[var(--color-paper)]">
                Wishlist
              </Link>
            </li>
          </ul>
        </div>

        <div>
          <span className="font-mono text-xs uppercase tracking-wide text-[var(--color-paper)]">Explore</span>
          <ul className="mt-4 space-y-2 text-xs">
            <li>
              <Link to="/" data-cursor className="hover:text-[var(--color-paper)]">
                Home
              </Link>
            </li>
            <li>
              <Link to="/reality" data-cursor className="hover:text-[var(--color-paper)]">
                Reality
              </Link>
            </li>
          </ul>
        </div>

        <div>
          <span className="font-mono text-xs uppercase tracking-wide text-[var(--color-paper)]">Info</span>
          <p className="mt-4 text-xs">13.08&deg;N 80.27&deg;E &mdash; Chennai, IN</p>
        </div>
      </div>

      <div className="font-mono mt-10 border-t border-white/10 pt-6 text-[11px] uppercase tracking-wide">
        &copy; {new Date().getFullYear()} Fsociety. All rights reserved.
      </div>
    </footer>
  );
}
