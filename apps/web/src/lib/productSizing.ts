export const APPAREL_SIZES = ["S", "M", "L", "XL", "XXL"] as const;

export type ProductSize = (typeof APPAREL_SIZES)[number];

const FOOTWEAR_CATEGORY_PATTERN = /\b(foot\s*wears?|shoes?|sneakers?|trainers?|boots?|sandals?|slippers?|heels?|flats?)\b/;

export function productUsesApparelSizes(categorySlug?: string | null, categoryName?: string | null) {
  const category = `${categorySlug ?? ""} ${categoryName ?? ""}`
    .replace(/[-_]+/g, " ")
    .toLowerCase();

  return !FOOTWEAR_CATEGORY_PATTERN.test(category);
}
