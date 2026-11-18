import { useSearchParams } from "react-router-dom";

import { FilterRail } from "@/components/product/FilterRail";
import { ProductGrid } from "@/components/product/ProductGrid";
import { AmbientGlow } from "@/components/ui/AmbientGlow";
import { Button } from "@/components/ui/Button";
import { StateMessage } from "@/components/ui/StateMessage";
import { useCategories, useProducts } from "@/hooks/useProducts";
import { parseShopFilters, serializeShopFilters } from "@/lib/shopFilters";
import type { ProductFilters } from "@/types/product";

export default function ShopPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const filters = parseShopFilters(searchParams);
  const updateFilters = (nextFilters: ProductFilters, options?: { replace?: boolean }) => {
    setSearchParams((current) => serializeShopFilters(nextFilters, current), options);
  };
  const { data: categories } = useCategories();
  const { data: products, isLoading, isError, refetch } = useProducts(filters);

  const page = filters.page ?? 1;
  const pageSize = products?.page_size ?? 20;
  const totalPages = products ? Math.max(1, Math.ceil(products.total / pageSize)) : 1;

  return (
    <div className="relative py-10 pb-24">
      <AmbientGlow />

      <h1 className="relative z-10 font-display text-4xl text-[var(--color-paper)]">Shop</h1>
      <p className="relative z-10 mt-2 text-sm text-[var(--color-steel)]">
        {products ? `${products.total} results found` : isError ? "" : "Loading"}
      </p>

      <div className="relative z-10 mt-6">
        <FilterRail categories={categories ?? []} filters={filters} onChange={updateFilters} />
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
                  onClick={() => updateFilters({ ...filters, page: page - 1 })}
                  className="rounded-full border border-white/10 px-4 py-2 text-sm text-[var(--color-steel)] disabled:opacity-30"
                >
                  Prev
                </button>
                <span className="text-sm text-[var(--color-steel)]">
                  Page {page} of {totalPages}
                </span>
                <button
                  data-cursor
                  disabled={page >= totalPages}
                  onClick={() => updateFilters({ ...filters, page: page + 1 })}
                  className="rounded-full border border-white/10 px-4 py-2 text-sm text-[var(--color-steel)] disabled:opacity-30"
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
