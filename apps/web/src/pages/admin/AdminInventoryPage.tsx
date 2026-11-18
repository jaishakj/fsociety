import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link, Navigate } from "react-router-dom";

import { useCustomerAuth } from "@/auth/customerAuth";
import { Button } from "@/components/ui/Button";
import { api, withAuth } from "@/lib/api";
import { productSizesForCategory, type ProductSize } from "@/lib/productSizing";
import type { Product, ProductListResponse } from "@/types/product";

const PAGE_SIZE = 50;
const MAX_STOCK = 2_147_483_647;

type VariantUpdate = {
  size: ProductSize;
  sku?: string;
  stock: number;
};

type InventoryUpdate = {
  stock?: number;
  variants?: VariantUpdate[];
};

type ProductListParams = {
  page: number;
  page_size: number;
  q?: string;
  status?: "draft" | "published" | "archived";
};

function errorMessage(error: unknown) {
  const response = typeof error === "object" && error !== null && "response" in error
    ? (error as { response?: { data?: { detail?: unknown } } }).response
    : undefined;
  if (typeof response?.data?.detail === "string") return response.data.detail;
  if (error instanceof Error && error.message) return error.message;
  return "Inventory could not be saved. Please try again.";
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    published: "border-emerald-300/20 bg-emerald-300/10 text-emerald-200",
    draft: "border-amber-300/20 bg-amber-300/10 text-amber-100",
    archived: "border-white/10 bg-white/5 text-[var(--color-steel)]",
  };

  return (
    <span className={`inline-flex min-h-7 items-center rounded-full border px-2.5 font-mono text-[10px] uppercase tracking-wider ${styles[status] ?? styles.archived}`}>
      {status}
    </span>
  );
}

export default function AdminInventoryPage() {
  const auth = useCustomerAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [searchError, setSearchError] = useState("");
  const [status, setStatus] = useState<ProductListParams["status"]>();

  const productsQuery = useQuery({
    queryKey: ["admin-products", page, search, status],
    enabled: auth.isLoaded && auth.isSignedIn && auth.isAdmin,
    queryFn: async () => {
      const token = await auth.getToken();
      if (!token) throw new Error("Your session has expired. Sign in again to continue.");
      const params: ProductListParams = {
        page,
        page_size: PAGE_SIZE,
        ...(search ? { q: search } : {}),
        ...(status ? { status } : {}),
      };
      const response = await api.get<ProductListResponse>("/admin/products", {
        ...withAuth(token),
        params,
      });
      return response.data;
    },
  });

  const saveInventory = useMutation({
    mutationFn: async ({ productId, update }: { productId: string; update: InventoryUpdate }) => {
      const token = await auth.getToken();
      if (!token) throw new Error("Your session has expired. Sign in again to continue.");
      const response = await api.put<Product>(
        `/admin/products/${productId}`,
        update,
        withAuth(token),
      );
      return response.data;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-products"] });
    },
  });

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextSearch = searchInput.trim();
    if (nextSearch.length === 1) {
      setSearchError("Enter at least two characters, or clear the search.");
      return;
    }
    setSearchError("");
    setSearch(nextSearch);
    setPage(1);
  }

  if (!auth.isLoaded) {
    return <p className="py-24 text-center text-sm text-[var(--color-steel)]">Checking access…</p>;
  }
  if (!auth.isSignedIn) return <Navigate to="/sign-in" replace />;
  if (!auth.isAdmin) {
    return (
      <section className="mx-auto max-w-2xl py-20 text-center">
        <p className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">FSOCIETY / ADMIN</p>
        <h1 className="mt-3 font-display text-3xl text-[var(--color-paper)]">Access restricted</h1>
        <p className="mt-3 text-sm leading-6 text-[var(--color-steel)]">This area is available to store administrators.</p>
        <Link className="mt-6 inline-flex min-h-12 items-center text-sm text-[var(--color-paper)] underline underline-offset-4" to="/">Return to the storefront</Link>
      </section>
    );
  }

  const products = productsQuery.data?.items ?? [];
  const totalPages = Math.max(1, Math.ceil((productsQuery.data?.total ?? 0) / PAGE_SIZE));

  return (
    <section className="mx-auto max-w-6xl py-10 sm:py-14">
      <header className="mb-8 border-b border-white/10 pb-6 sm:mb-10 sm:pb-8">
        <p className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">FSOCIETY / STORE OPERATIONS</p>
        <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl text-[var(--color-paper)] sm:text-4xl">Inventory</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--color-steel)]">
              Set confirmed stock by size. Blank sizes stay unconfigured, and existing quantities are preserved.
            </p>
          </div>
          <span className="font-mono text-xs text-[var(--color-steel)]">
            {productsQuery.data ? `${productsQuery.data.total} products` : "Product catalogue"}
          </span>
        </div>
      </header>

      <div className="rounded-3xl border border-white/10 bg-[var(--color-panel)] p-4 sm:p-6">
        <form onSubmit={submitSearch} className="grid gap-3 border-b border-white/10 pb-5 sm:grid-cols-[minmax(0,1fr)_12rem_auto] sm:items-end">
          <label className="grid gap-2 text-sm text-[var(--color-steel)]" htmlFor="inventory-search">
            Find a product
            <input
              id="inventory-search"
              type="search"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search by name"
              maxLength={100}
              aria-describedby={searchError ? "inventory-search-error" : undefined}
              className="min-h-12 min-w-0 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] placeholder:text-[var(--color-steel)]/65 focus:border-[var(--color-signal)] focus:outline-none"
            />
          </label>
          <label className="grid gap-2 text-sm text-[var(--color-steel)]" htmlFor="inventory-status">
            Product status
            <select
              id="inventory-status"
              value={status ?? "all"}
              onChange={(event) => {
                const nextStatus = event.target.value;
                setStatus(nextStatus === "all" ? undefined : nextStatus as ProductListParams["status"]);
                setPage(1);
              }}
              className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] focus:border-[var(--color-signal)] focus:outline-none"
            >
              <option value="all">All statuses</option>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="archived">Archived</option>
            </select>
          </label>
          <Button type="submit" variant="outline" className="min-h-12">Search</Button>
        </form>
        {searchError ? <p id="inventory-search-error" role="alert" className="mt-3 text-sm text-[var(--color-signal)]">{searchError}</p> : null}

        {productsQuery.isPending ? (
          <p role="status" className="py-12 text-center text-sm text-[var(--color-steel)]">Loading products…</p>
        ) : productsQuery.isError ? (
          <div role="alert" className="py-10 text-center">
            <p className="text-sm text-[var(--color-signal)]">{errorMessage(productsQuery.error)}</p>
            <Button type="button" variant="outline" className="mt-4" onClick={() => void productsQuery.refetch()}>Try again</Button>
          </div>
        ) : products.length === 0 ? (
          <p className="py-12 text-center text-sm text-[var(--color-steel)]">No products match those filters.</p>
        ) : (
          <>
            <ul aria-label="Products and inventory" className="divide-y divide-white/10">
              {products.map((product) => (
                <li key={product.id} className="py-4 first:pt-5 last:pb-1 sm:py-5">
                  <ProductInventoryEditor
                    product={product}
                    saving={saveInventory.isPending && saveInventory.variables?.productId === product.id}
                    onSave={async (update) => {
                      await saveInventory.mutateAsync({ productId: product.id, update });
                    }}
                  />
                </li>
              ))}
            </ul>

            <nav aria-label="Product pages" className="mt-6 flex items-center justify-between border-t border-white/10 pt-5">
              <p className="text-xs text-[var(--color-steel)]">Page {page} of {totalPages}</p>
              <div className="flex gap-2">
                <Button type="button" variant="outline" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>Previous</Button>
                <Button type="button" variant="outline" disabled={page >= totalPages} onClick={() => setPage((current) => current + 1)}>Next</Button>
              </div>
            </nav>
          </>
        )}
      </div>
    </section>
  );
}

function ProductInventoryEditor({
  product,
  saving,
  onSave,
}: {
  product: Product;
  saving: boolean;
  onSave: (update: InventoryUpdate) => Promise<void>;
}) {
  const sizes = productSizesForCategory(product.category.slug, product.category.name);
  const [expanded, setExpanded] = useState(false);
  const [unitStock, setUnitStock] = useState(String(product.stock));
  const [sizeStock, setSizeStock] = useState<Record<string, string>>(() => Object.fromEntries(
    sizes.map((size) => [size, String(product.variants?.find((variant) => variant.size === size)?.stock ?? "")]),
  ));
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const variantBySize = new Map((product.variants ?? []).map((variant) => [variant.size, variant]));
  const hasConfiguredVariants = (product.variants ?? []).length > 0;

  async function submitInventory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSaved(false);

    if (sizes.length === 0) {
      const stock = Number(unitStock);
      if (!Number.isSafeInteger(stock) || stock < 0 || stock > MAX_STOCK) {
        setError(`Enter a whole number between 0 and ${MAX_STOCK}.`);
        return;
      }
      try {
        await onSave({ stock });
        setSaved(true);
      } catch (reason) {
        setError(errorMessage(reason));
      }
      return;
    }

    if (!hasConfiguredVariants) {
      const missingSize = sizes.find((size) => !sizeStock[size]?.trim());
      if (missingSize) {
        setError(`Enter a confirmed count for every size before converting aggregate stock. Use 0 for sizes with none; ${missingSize} is still blank.`);
        return;
      }
    }

    const invalidSize = sizes.find((size) => {
      const value = sizeStock[size]?.trim() ?? "";
      if (!value) return false;
      const stock = Number(value);
      return !Number.isSafeInteger(stock) || stock < 0 || stock > MAX_STOCK;
    });
    if (invalidSize) {
      setError(`${invalidSize} stock must be a whole number between 0 and ${MAX_STOCK}.`);
      return;
    }

    const variants = sizes.flatMap((size): VariantUpdate[] => {
      const existing = variantBySize.get(size);
      const value = sizeStock[size]?.trim() ?? "";
      if (!value) {
        return existing ? [{ size, sku: existing.sku, stock: existing.stock }] : [];
      }
      return [{ size, ...(existing ? { sku: existing.sku } : {}), stock: Number(value) }];
    });
    if (variants.length === 0) {
      setError("Enter confirmed stock for at least one size. Leave unknown sizes blank.");
      return;
    }

    try {
      const update: InventoryUpdate = { variants };
      if (!hasConfiguredVariants) {
        update.stock = variants.reduce((sum, variant) => sum + variant.stock, 0);
      }
      await onSave(update);
      setSizeStock((current) => Object.fromEntries(sizes.map((size) => {
        const value = current[size]?.trim() ?? "";
        const existing = variantBySize.get(size);
        return [size, value || (existing ? String(existing.stock) : "")];
      })));
      setSaved(true);
    } catch (reason) {
      setError(errorMessage(reason));
    }
  }

  const editorId = `inventory-${product.id}`;
  const total = sizes.length > 0
    ? (product.variants ?? []).reduce((sum, variant) => sum + variant.stock, 0)
    : product.stock;
  const stockSummary = sizes.length === 0
    ? `${total} units`
    : product.variants?.length
      ? `${total} units across sizes`
      : `${product.stock} legacy units · size split not set`;

  return (
    <article>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2.5">
            <h2 className="min-w-0 break-words font-display text-lg text-[var(--color-paper)]">{product.name}</h2>
            <StatusBadge status={product.status} />
          </div>
          <p className="mt-1 text-xs text-[var(--color-steel)]">
            {product.category.name} <span aria-hidden="true">·</span> {product.slug}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="max-w-48 text-right font-mono text-[10px] leading-5 text-[var(--color-steel)] sm:max-w-none sm:text-xs">
            {stockSummary}
          </span>
          <button
            type="button"
            aria-expanded={expanded}
            aria-controls={expanded ? editorId : undefined}
            onClick={() => setExpanded((current) => !current)}
            className="inline-flex min-h-11 items-center rounded-full border border-white/15 px-4 text-xs text-[var(--color-paper)] transition-colors hover:border-[var(--color-signal)] hover:bg-white/5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-signal)]"
          >
            {expanded ? "Close" : "Edit stock"}
          </button>
        </div>
      </div>

      {expanded ? (
        <form id={editorId} onSubmit={(event) => void submitInventory(event)} className="mt-5 rounded-2xl border border-white/10 bg-[var(--color-void)]/70 p-4 sm:p-5">
          {sizes.length > 0 ? (
            <>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
                {sizes.map((size) => {
                  const inputId = `${editorId}-${size}`;
                  const existing = variantBySize.get(size);
                  return (
                    <label key={size} htmlFor={inputId} className="grid gap-2 text-xs text-[var(--color-steel)]">
                      <span className="font-mono uppercase tracking-wider">Size {size}</span>
                      <input
                        id={inputId}
                        type="number"
                        inputMode="numeric"
                        min="0"
                        max={MAX_STOCK}
                        step="1"
                        required={!hasConfiguredVariants}
                        value={sizeStock[size] ?? ""}
                        onChange={(event) => setSizeStock((current) => ({ ...current, [size]: event.target.value }))}
                        aria-describedby={`${editorId}-stock-help`}
                        className="min-h-12 min-w-0 rounded-xl border border-white/10 bg-[var(--color-panel)] px-3 text-base text-[var(--color-paper)] focus:border-[var(--color-signal)] focus:outline-none"
                      />
                      {existing ? <span className="sr-only">Existing stock: {existing.stock}</span> : null}
                    </label>
                  );
                })}
              </div>
              <p id={`${editorId}-stock-help`} className="mt-4 text-xs leading-5 text-[var(--color-steel)]">
                {hasConfiguredVariants
                  ? "Enter only counts you have confirmed. Blank sizes remain unconfigured; existing quantities are kept if their fields are cleared."
                  : `Stock is currently recorded as ${product.stock} aggregate units. Enter a confirmed count for every size, including 0 where none are available, to create the size breakdown.`}
              </p>
            </>
          ) : (
            <label htmlFor={`${editorId}-units`} className="grid max-w-xs gap-2 text-sm text-[var(--color-steel)]">
              Units in stock
              <input
                id={`${editorId}-units`}
                type="number"
                inputMode="numeric"
                min="0"
                max={MAX_STOCK}
                step="1"
                value={unitStock}
                onChange={(event) => setUnitStock(event.target.value)}
                className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-panel)] px-4 text-base text-[var(--color-paper)] focus:border-[var(--color-signal)] focus:outline-none"
              />
            </label>
          )}
          <div className="mt-5 flex flex-wrap items-center gap-3">
            <Button type="submit" disabled={saving}>
              {saving ? "Saving…" : "Save inventory"}
            </Button>
            {saved ? <p role="status" className="text-sm text-emerald-200">Inventory saved.</p> : null}
            {error ? <p role="alert" className="w-full text-sm text-[var(--color-signal)]">{error}</p> : null}
          </div>
        </form>
      ) : null}
    </article>
  );
}
