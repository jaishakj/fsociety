import type { Category, ProductFilters } from "@/types/product";

interface FilterRailProps {
  categories: Category[];
  filters: ProductFilters;
  onChange: (filters: ProductFilters) => void;
}

export function FilterRail({ categories, filters, onChange }: FilterRailProps) {
  return (
    <aside className="font-mono rounded-2xl border border-white/10 bg-[var(--color-panel)] p-4 text-xs uppercase tracking-wide text-[var(--color-steel)]">
      <div className="flex flex-wrap items-center gap-2">
        <button
          data-cursor
          onClick={() => onChange({ ...filters, category: undefined, page: 1 })}
          className={`rounded-full border px-3 py-1 transition-colors ${
            !filters.category ? "border-[var(--color-signal)] text-[var(--color-signal)]" : "border-white/10"
          }`}
        >
          All
        </button>
        {categories.map((category) => (
          <button
            key={category.id}
            data-cursor
            onClick={() => onChange({ ...filters, category: category.slug, page: 1 })}
            className={`rounded-full border px-3 py-1 transition-colors ${
              filters.category === category.slug
                ? "border-[var(--color-signal)] text-[var(--color-signal)]"
                : "border-white/10"
            }`}
          >
            {category.name}
          </button>
        ))}
        <select
          data-cursor
          value={filters.sort ?? "newest"}
          onChange={(e) => onChange({ ...filters, sort: e.target.value as ProductFilters["sort"] })}
          className="ml-auto rounded-full border border-white/10 bg-transparent px-3 py-1 text-[var(--color-paper)]"
        >
          <option value="newest">Newest</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
        </select>
      </div>

      <div className="mt-3 flex items-center gap-2 border-t border-white/10 pt-3">
        <span>Price</span>
        <input
          type="number"
          min={0}
          placeholder="Min"
          data-cursor
          value={filters.min_price ?? ""}
          onChange={(e) =>
            onChange({ ...filters, min_price: e.target.value ? Number(e.target.value) : undefined, page: 1 })
          }
          className="w-20 rounded-full border border-white/10 bg-transparent px-3 py-1 text-[var(--color-paper)] placeholder:text-[var(--color-steel)]"
        />
        <span>&ndash;</span>
        <input
          type="number"
          min={0}
          placeholder="Max"
          data-cursor
          value={filters.max_price ?? ""}
          onChange={(e) =>
            onChange({ ...filters, max_price: e.target.value ? Number(e.target.value) : undefined, page: 1 })
          }
          className="w-20 rounded-full border border-white/10 bg-transparent px-3 py-1 text-[var(--color-paper)] placeholder:text-[var(--color-steel)]"
        />
        {filters.min_price || filters.max_price ? (
          <button
            data-cursor
            onClick={() => onChange({ ...filters, min_price: undefined, max_price: undefined, page: 1 })}
            className="text-[var(--color-signal)]"
          >
            Clear
          </button>
        ) : null}
      </div>
    </aside>
  );
}
