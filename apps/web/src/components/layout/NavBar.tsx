import { Heart, Instagram, Search, ShoppingBag } from "lucide-react";
import { Link } from "react-router-dom";

export function NavBar() {
  return (
    <header className="sticky top-4 z-40 mx-auto flex max-w-6xl items-center justify-between rounded-full border border-white/10 bg-[var(--color-panel)]/80 px-6 py-3 backdrop-blur">
      <Link
        to="/"
        data-cursor
        className="font-display text-lg tracking-tight text-[var(--color-paper)]"
      >
        FSOCIETY
      </Link>

      <nav className="hidden gap-6 text-sm text-[var(--color-steel)] md:flex">
        <Link to="/" data-cursor className="transition-colors hover:text-[var(--color-paper)]">
          Home
        </Link>
        <Link to="/shop" data-cursor className="transition-colors hover:text-[var(--color-paper)]">
          Shop
        </Link>
      </nav>

      <div className="flex items-center gap-2 text-[var(--color-paper)]">
        <button data-cursor aria-label="Search" className="rounded-full p-2 hover:bg-white/5">
          <Search size={18} />
        </button>
        <button data-cursor aria-label="Wishlist" className="rounded-full p-2 hover:bg-white/5">
          <Heart size={18} />
        </button>
        <button data-cursor aria-label="Bag" className="rounded-full p-2 hover:bg-white/5">
          <ShoppingBag size={18} />
        </button>
        <a
          href="https://instagram.com"
          data-cursor
          aria-label="Instagram"
          className="rounded-full p-2 hover:bg-white/5"
        >
          <Instagram size={18} />
        </a>
      </div>
    </header>
  );
}
