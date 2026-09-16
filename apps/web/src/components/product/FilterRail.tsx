import type { Category, ProductFilters } from "@/types/product";

interface FilterRailProps {
  categories: Category[];
  filters: ProductFilters;
  onChange: (filters: ProductFilters) => void;
}

export function FilterRail({ categories, filters, onChange }: FilterRailProps) {
  return (
    <aside className="font-mono flex flex-wrap items-center gap-2 rounded-2xl border border-white/10 bg-[var(--color-panel)] p-4 text-xs uppercase tracking-wide text-[var(--color-steel)]">
      <button
        data-cursor
        onClick={() => onChange({ ...filters, category: undefined })}
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
          onClick={() => onChange({ ...filters, category: category.slug })}
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
    </aside>
  );
}
