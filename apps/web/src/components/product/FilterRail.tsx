import type { Category, ProductFilters } from "@/types/product";
import { OriginDropdown } from "@/components/ui/origin-dropdown";

interface FilterRailProps {
  categories: Category[];
  filters: ProductFilters;
  onChange: (filters: ProductFilters) => void;
}

export function FilterRail({ categories, filters, onChange }: FilterRailProps) {
  const sortOptions = [
    { value: "newest", label: "Newest" },
    { value: "price_asc", label: "Price: Low to High" },
    { value: "price_desc", label: "Price: High to Low" },
  ] as const;
  const selectedSort = sortOptions.find((option) => option.value === (filters.sort ?? "newest")) ?? sortOptions[0];

  return (
    <aside aria-label="Product filters" className="rounded-2xl border border-white/10 bg-[var(--color-panel)] p-4 text-sm text-[var(--color-steel)]">
      <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:gap-2">
        <div role="group" aria-label="Filter by category" className="mobile-filter-scroll -mx-4 flex max-w-[calc(100%+2rem)] gap-2 overflow-x-auto px-4 pb-1 sm:mx-0 sm:max-w-full sm:flex-wrap sm:overflow-visible sm:px-0 sm:pb-0">
          <button
            data-cursor
            type="button"
            aria-pressed={!filters.category}
            onClick={() => onChange({ ...filters, category: undefined, page: 1 })}
            className={`min-h-12 rounded-full border px-4 transition-colors ${
              !filters.category ? "border-[var(--color-signal)] bg-[var(--color-signal)]/10 text-[var(--color-signal)]" : "border-white/10 hover:bg-white/5"
            }`}
          >
            All
          </button>
          {categories.map((category) => (
            <button
              key={category.id}
              data-cursor
              type="button"
              aria-pressed={filters.category === category.slug}
              onClick={() => onChange({ ...filters, category: category.slug, page: 1 })}
              className={`min-h-12 rounded-full border px-4 transition-colors ${
                filters.category === category.slug
                  ? "border-[var(--color-signal)] bg-[var(--color-signal)]/10 text-[var(--color-signal)]"
                  : "border-white/10 hover:bg-white/5"
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>
        <OriginDropdown
          side="bottom"
          align="end"
          triggerAriaLabel={`Sort products: ${selectedSort.label}`}
          trigger={<span>{selectedSort.label}</span>}
          className="sm:ml-auto"
          items={sortOptions.map((option) => ({
            id: option.value,
            label: option.label,
            selected: selectedSort.value === option.value,
            onSelect: () => onChange({ ...filters, sort: option.value as ProductFilters["sort"] }),
          }))}
        />
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-white/10 pt-3">
        <span className="mr-1">Price range</span>
        <input
          aria-label="Minimum price"
          type="number"
          min={0}
          placeholder="Min"
          data-cursor
          value={filters.min_price ?? ""}
          onChange={(e) =>
            onChange({ ...filters, min_price: e.target.value ? Number(e.target.value) : undefined, page: 1 })
          }
          className="min-h-12 w-24 rounded-xl border border-white/10 bg-[var(--color-void)] px-3 text-[var(--color-paper)] placeholder:text-[var(--color-steel)]"
        />
        <span>&ndash;</span>
        <input
          aria-label="Maximum price"
          type="number"
          min={0}
          placeholder="Max"
          data-cursor
          value={filters.max_price ?? ""}
          onChange={(e) =>
            onChange({ ...filters, max_price: e.target.value ? Number(e.target.value) : undefined, page: 1 })
          }
          className="min-h-12 w-24 rounded-xl border border-white/10 bg-[var(--color-void)] px-3 text-[var(--color-paper)] placeholder:text-[var(--color-steel)]"
        />
        {filters.min_price || filters.max_price ? (
          <button
            data-cursor
            type="button"
            onClick={() => onChange({ ...filters, min_price: undefined, max_price: undefined, page: 1 })}
            className="min-h-12 rounded-full px-3 text-[var(--color-signal)] hover:bg-white/5"
          >
            Clear
          </button>
        ) : null}
      </div>
    </aside>
  );
}
