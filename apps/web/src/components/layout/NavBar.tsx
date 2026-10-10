import { AnimatePresence, motion } from "motion/react";
import { Heart, Instagram, Menu, Search, ShoppingBag, X } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { useCartStore } from "@/stores/cartStore";
import { useSearchStore } from "@/stores/searchStore";
import { useWishlistStore } from "@/stores/wishlistStore";

const NAV_LINKS = [
  { to: "/", label: "Home" },
  { to: "/shop", label: "Shop" },
  { to: "/reality", label: "Reality" },
  { to: "/wishlist", label: "Wishlist" },
];

export function NavBar() {
  const cartCount = useCartStore((state) => state.totalCount());
  const toggleCart = useCartStore((state) => state.toggle);
  const wishlistCount = useWishlistStore((state) => state.items.length);
  const openSearch = useSearchStore((state) => state.open);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <header className="sticky top-4 z-40 mx-auto flex max-w-6xl items-center justify-between rounded-full border border-white/10 bg-[var(--color-panel)]/80 px-6 py-3 backdrop-blur">
        <Link to="/" data-cursor className="font-display text-lg tracking-tight text-[var(--color-paper)]">
          FSOCIETY
        </Link>

        <nav className="hidden gap-6 text-sm text-[var(--color-steel)] md:flex">
          {NAV_LINKS.filter((link) => link.label !== "Wishlist").map((link) => (
            <Link key={link.to} to={link.to} data-cursor className="transition-colors hover:text-[var(--color-paper)]">
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-1 text-[var(--color-paper)] md:gap-2">
          <button data-cursor aria-label="Search" onClick={openSearch} className="rounded-full p-2 hover:bg-white/5">
            <Search size={18} />
          </button>
          <Link
            to="/wishlist"
            data-cursor
            aria-label="Wishlist"
            className="relative rounded-full p-2 hover:bg-white/5"
          >
            <Heart size={18} />
            {wishlistCount > 0 ? (
              <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--color-signal)] text-[9px] font-bold text-[var(--color-void)]">
                {wishlistCount}
              </span>
            ) : null}
          </Link>
          <button
            data-cursor
            aria-label="Bag"
            onClick={toggleCart}
            className="relative rounded-full p-2 hover:bg-white/5"
          >
            <ShoppingBag size={18} />
            {cartCount > 0 ? (
              <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--color-signal)] text-[9px] font-bold text-[var(--color-void)]">
                {cartCount}
              </span>
            ) : null}
          </button>
          <a
            href="https://instagram.com"
            data-cursor
            aria-label="Instagram"
            className="hidden rounded-full p-2 hover:bg-white/5 md:inline-flex"
          >
            <Instagram size={18} />
          </a>
          <button
            data-cursor
            aria-label="Menu"
            onClick={() => setMobileOpen(true)}
            className="rounded-full p-2 hover:bg-white/5 md:hidden"
          >
            <Menu size={18} />
          </button>
        </div>
      </header>

      <AnimatePresence>
        {mobileOpen ? (
          <>
            <motion.div
              className="fixed inset-0 z-[997] bg-black/60 md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
            />
            <motion.div
              className="fixed inset-x-4 top-4 z-[998] rounded-3xl border border-white/10 bg-[var(--color-panel)] p-6 md:hidden"
              initial={{ opacity: 0, y: -16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ type: "spring", bounce: 0, duration: 0.3 }}
            >
              <div className="flex items-center justify-between">
                <span className="font-display text-lg text-[var(--color-paper)]">FSOCIETY</span>
                <button data-cursor aria-label="Close menu" onClick={() => setMobileOpen(false)}>
                  <X size={20} className="text-[var(--color-steel)]" />
                </button>
              </div>
              <nav className="mt-6 flex flex-col gap-4">
                {NAV_LINKS.map((link) => (
                  <Link
                    key={link.to}
                    to={link.to}
                    data-cursor
                    onClick={() => setMobileOpen(false)}
                    className="font-display text-2xl text-[var(--color-paper)]"
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>
            </motion.div>
          </>
        ) : null}
      </AnimatePresence>
    </>
  );
}
