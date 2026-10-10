import { useState } from "react";

import { FilterRail } from "@/components/product/FilterRail";
import { ProductGrid } from "@/components/product/ProductGrid";
import { AmbientGlow } from "@/components/ui/AmbientGlow";
import { Button } from "@/components/ui/Button";
import { StateMessage } from "@/components/ui/StateMessage";
import { useCategories, useProducts } from "@/hooks/useProducts";
import type { ProductFilters } from "@/types/product";

export default function ShopPage() {
  const [filters, setFilters] = useState<ProductFilters>({ page: 1, sort: "newest" });
  const { data: categories } = useCategories();
  const { data: products, isLoading, isError, refetch } = useProducts(filters);

  const page = filters.page ?? 1;
  const pageSize = products?.page_size ?? 20;
  const totalPages = products ? Math.max(1, Math.ceil(products.total / pageSize)) : 1;

  return (
    <div className="relative py-10 pb-24">
      <AmbientGlow />

      <h1 className="relative z-10 font-display text-4xl text-[var(--color-paper)]">Shop</h1>
      <p className="font-mono relative z-10 mt-2 text-xs uppercase tracking-wide text-[var(--color-steel)]">
        {products ? `${products.total} results found` : isError ? "" : "Loading"}
      </p>

      <div className="relative z-10 mt-6">
        <FilterRail categories={categories ?? []} filters={filters} onChange={setFilters} />
      </div>

      <div className="relative z-10 mt-8">
        {isError ? (
          <StateMessage
            title="Couldn't load products"
            description="Something went wrong reaching the store. Try again in a moment."
            action={
              <Button variant="outline" data-cursor onClick={() => refetch()}>
                Retry
              </Button>
            }
          />
        ) : isLoading ? (
          <p className="text-[var(--color-steel)]">Loading products&hellip;</p>
        ) : (
          <>
            <ProductGrid products={products?.items ?? []} />
            {totalPages > 1 ? (
              <div className="mt-10 flex items-center justify-center gap-4">
                <button
                  data-cursor
                  disabled={page <= 1}
                  onClick={() => setFilters((prev) => ({ ...prev, page: page - 1 }))}
                  className="font-mono rounded-full border border-white/10 px-4 py-2 text-xs uppercase tracking-wide text-[var(--color-steel)] disabled:opacity-30"
                >
                  Prev
                </button>
                <span className="font-mono text-xs text-[var(--color-steel)]">
                  Page {page} of {totalPages}
                </span>
                <button
                  data-cursor
                  disabled={page >= totalPages}
                  onClick={() => setFilters((prev) => ({ ...prev, page: page + 1 }))}
                  className="font-mono rounded-full border border-white/10 px-4 py-2 text-xs uppercase tracking-wide text-[var(--color-steel)] disabled:opacity-30"
                >
                  Next
                </button>
              </div>
            ) : null}
          </>
        )}
      </div>
    </div>
  );
}
