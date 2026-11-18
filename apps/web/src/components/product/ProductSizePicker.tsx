import type { ProductSize } from "@/lib/productSizing";

interface ProductSizePickerProps {
  sizes: readonly ProductSize[];
  value: ProductSize | null;
  onChange: (size: ProductSize) => void;
  unavailableSizes?: readonly ProductSize[];
}

export function ProductSizePicker({ sizes, value, onChange, unavailableSizes = [] }: ProductSizePickerProps) {
  return (
    <div>
      <p className="mb-3 text-sm text-[var(--color-steel)]">Choose a size</p>
      <div role="group" aria-label="Available sizes" className="flex flex-wrap gap-2">
        {sizes.map((size) => {
          const unavailable = unavailableSizes.includes(size);
          return (
            <button
              key={size}
              type="button"
              data-cursor
              disabled={unavailable}
              aria-pressed={value === size}
              aria-label={unavailable ? `${size}, out of stock` : size}
              onClick={() => onChange(size)}
              className={`flex min-h-12 min-w-12 items-center justify-center rounded-full border px-4 text-sm transition-colors ${
                value === size
                  ? "border-[var(--color-signal)] bg-[var(--color-signal)]/10 text-[var(--color-signal)]"
                  : unavailable
                    ? "cursor-not-allowed border-white/10 text-[var(--color-steel)] opacity-45"
                    : "border-white/10 text-[var(--color-paper)] hover:bg-white/5"
              }`}
            >
              <span className={unavailable ? "line-through" : undefined}>{size}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
