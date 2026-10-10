import { AnimatePresence, motion } from "motion/react";
import { Search, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useProducts } from "@/hooks/useProducts";
import { useSearchStore } from "@/stores/searchStore";

export function SearchModal() {
  const isOpen = useSearchStore((state) => state.isOpen);
  const close = useSearchStore((state) => state.close);
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timeout);
  }, [query]);

  useEffect(() => {
    if (!isOpen) setQuery("");
  }, [isOpen]);

  const { data, isLoading } = useProducts(
    debouncedQuery.length > 1 ? { q: debouncedQuery, page_size: 8 } : {},
  );
  const results = debouncedQuery.length > 1 ? (data?.items ?? []) : [];

  return (
    <AnimatePresence>
      {isOpen ? (
        <>
          <motion.div
            className="fixed inset-0 z-[997] bg-black/60"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={close}
          />
          <motion.div
            className="fixed inset-x-4 top-24 z-[998] mx-auto max-w-xl rounded-3xl border border-white/10 bg-[var(--color-panel)] p-4"
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ type: "spring", bounce: 0, duration: 0.3 }}
          >
            <div className="flex items-center gap-3 rounded-full border border-white/10 bg-black/30 px-4 py-3">
              <Search size={18} className="text-[var(--color-steel)]" />
              <input
                autoFocus
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search products..."
                className="flex-1 bg-transparent text-sm text-[var(--color-paper)] placeholder:text-[var(--color-steel)] focus:outline-none"
              />
              <button type="button" data-cursor onClick={close} aria-label="Close search">
                <X size={18} className="text-[var(--color-steel)]" />
              </button>
            </div>

            <div className="mt-4 max-h-96 overflow-y-auto">
              {debouncedQuery.length <= 1 ? (
                <p className="py-6 text-center text-sm text-[var(--color-steel)]">
                  Type at least 2 characters to search.
                </p>
              ) : isLoading ? (
                <p className="py-6 text-center text-sm text-[var(--color-steel)]">Searching&hellip;</p>
              ) : results.length === 0 ? (
                <p className="py-6 text-center text-sm text-[var(--color-steel)]">
                  No products match &ldquo;{debouncedQuery}&rdquo;.
                </p>
              ) : (
                <ul className="space-y-2">
                  {results.map((product) => (
                    <li key={product.id}>
                      <Link
                        to={`/product/${product.slug}`}
                        data-cursor
                        onClick={close}
                        className="flex items-center gap-3 rounded-2xl p-2 hover:bg-white/5"
                      >
                        {product.images[0]?.url ? (
                          <img
                            src={product.images[0].url}
                            alt={product.name}
                            className="h-12 w-10 rounded-lg object-cover"
                          />
                        ) : (
                          <div className="h-12 w-10 rounded-lg bg-black/40" />
                        )}
                        <span className="flex-1 text-sm text-[var(--color-paper)]">{product.name}</span>
                        <span className="font-mono text-xs text-[var(--color-signal)]">
                          {product.currency} {product.price}
                        </span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </motion.div>
        </>
      ) : null}
    </AnimatePresence>
  );
}
