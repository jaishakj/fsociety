export const APPAREL_SIZES = ["S", "M", "L", "XL", "XXL"] as const;
export const DRESS_SIZES = ["XS", ...APPAREL_SIZES] as const;

export type ProductSize = (typeof DRESS_SIZES)[number];

const FOOTWEAR_CATEGORY_PATTERN = /\b(foot\s*wears?|shoes?|sneakers?|trainers?|boots?|sandals?|slippers?|heels?|flats?)\b/;
const DRESS_CATEGORY_PATTERN = /\bdresses?\b/;

function normalizedCategory(categorySlug?: string | null, categoryName?: string | null) {
  return `${categorySlug ?? ""} ${categoryName ?? ""}`
    .replace(/[-_]+/g, " ")
    .toLowerCase();
}

export function productUsesApparelSizes(categorySlug?: string | null, categoryName?: string | null) {
  return !FOOTWEAR_CATEGORY_PATTERN.test(normalizedCategory(categorySlug, categoryName));
}

export function productSizesForCategory(categorySlug?: string | null, categoryName?: string | null): readonly ProductSize[] {
  const category = normalizedCategory(categorySlug, categoryName);

  if (FOOTWEAR_CATEGORY_PATTERN.test(category)) return [];
  if (DRESS_CATEGORY_PATTERN.test(category)) return DRESS_SIZES;

  return APPAREL_SIZES;
}
