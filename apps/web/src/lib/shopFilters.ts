import type { ProductFilters } from "@/types/product";

const FILTER_KEYS = ["page", "category", "q", "min_price", "max_price", "sort"] as const;
const SORT_OPTIONS = ["newest", "price_asc", "price_desc"] as const;
type ProductSort = (typeof SORT_OPTIONS)[number];

function parsePage(value: string | null): number {
  if (value === null || value.trim() === "") return 1;
  const page = Number(value);
  return Number.isSafeInteger(page) && page >= 1 ? page : 1;
}

function parsePrice(value: string | null): number | undefined {
  if (value === null || value.trim() === "") return undefined;
  const price = Number(value);
  return Number.isFinite(price) && price >= 0 ? price : undefined;
}

function parseSort(value: string | null): ProductSort {
  return SORT_OPTIONS.includes(value as ProductSort) ? (value as ProductSort) : "newest";
}

function parseSearch(value: string | null): string | undefined {
  const query = value?.trim();
  return query && query.length >= 2 && query.length <= 100 ? query : undefined;
}

export function parseShopFilters(params: URLSearchParams): ProductFilters {
  const category = params.get("category")?.trim();
  const filters: ProductFilters = {
    page: parsePage(params.get("page")),
    sort: parseSort(params.get("sort")),
  };

  if (category) filters.category = category;

  const query = parseSearch(params.get("q"));
  if (query) filters.q = query;

  const minPrice = parsePrice(params.get("min_price"));
  if (minPrice !== undefined) filters.min_price = minPrice;

  const maxPrice = parsePrice(params.get("max_price"));
  if (maxPrice !== undefined) filters.max_price = maxPrice;

  return filters;
}

export function serializeShopFilters(
  filters: ProductFilters,
  currentParams: URLSearchParams = new URLSearchParams(),
): URLSearchParams {
  const params = new URLSearchParams(currentParams);
  for (const key of FILTER_KEYS) params.delete(key);

  const page = parsePage(filters.page === undefined ? null : String(filters.page));
  if (page > 1) params.set("page", String(page));

  const category = filters.category?.trim();
  if (category) params.set("category", category);

  const query = parseSearch(filters.q ?? null);
  if (query) params.set("q", query);

  const minPrice = parsePrice(filters.min_price === undefined ? null : String(filters.min_price));
  if (minPrice !== undefined) params.set("min_price", String(minPrice));

  const maxPrice = parsePrice(filters.max_price === undefined ? null : String(filters.max_price));
  if (maxPrice !== undefined) params.set("max_price", String(maxPrice));

  const sort = parseSort(filters.sort ?? null);
  if (sort !== "newest") params.set("sort", sort);

  return params;
}
