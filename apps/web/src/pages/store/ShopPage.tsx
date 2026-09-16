import { useState } from "react";

import { FilterRail } from "@/components/product/FilterRail";
import { ProductGrid } from "@/components/product/ProductGrid";
import { useCategories, useProducts } from "@/hooks/useProducts";
import type { ProductFilters } from "@/types/product";

export default function ShopPage() {
  const [filters, setFilters] = useState<ProductFilters>({ page: 1, sort: "newest" });
  const { data: categories } = useCategories();
  const { data: products, isLoading } = useProducts(filters);

  return (
    <div className="py-10">
      <h1 className="font-display text-4xl text-[var(--color-paper)]">Shop</h1>
      <p className="font-mono mt-2 text-xs uppercase tracking-wide text-[var(--color-steel)]">
        {products ? `${products.total} results found` : "Loading"}
      </p>

      <div className="mt-6">
        <FilterRail categories={categories ?? []} filters={filters} onChange={setFilters} />
      </div>

      <div className="mt-8">
        {isLoading ? (
          <p className="text-[var(--color-steel)]">Loading products…</p>
        ) : (
          <ProductGrid products={products?.items ?? []} />
        )}
      </div>
    </div>
  );
}
