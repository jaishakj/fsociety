import { APPAREL_SIZES, type ProductSize } from "@/lib/productSizing";

interface ProductSizePickerProps {
  value: ProductSize | null;
  onChange: (size: ProductSize) => void;
}

export function ProductSizePicker({ value, onChange }: ProductSizePickerProps) {
  return (
    <div>
      <p className="mb-3 text-sm text-[var(--color-steel)]">Choose a size</p>
      <div role="group" aria-label="Available sizes" className="flex flex-wrap gap-2">
        {APPAREL_SIZES.map((size) => (
          <button
            key={size}
            type="button"
            data-cursor
            aria-pressed={value === size}
            onClick={() => onChange(size)}
            className={`flex min-h-12 min-w-12 items-center justify-center rounded-full border px-4 text-sm transition-colors ${
              value === size
                ? "border-[var(--color-signal)] bg-[var(--color-signal)]/10 text-[var(--color-signal)]"
                : "border-white/10 text-[var(--color-paper)] hover:bg-white/5"
            }`}
          >
            {size}
          </button>
        ))}
      </div>
    </div>
  );
}
