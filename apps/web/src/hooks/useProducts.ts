import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { Category, Product, ProductFilters, ProductListResponse } from "@/types/product";

export function useProducts(filters: ProductFilters = {}) {
  return useQuery({
    queryKey: ["products", filters],
    queryFn: async () => {
      const { data } = await api.get<ProductListResponse>("/products", { params: filters });
      return data;
    },
  });
}

export function useProduct(slug: string | undefined) {
  return useQuery({
    queryKey: ["product", slug],
    queryFn: async () => {
      const { data } = await api.get<Product>(`/products/${slug}`);
      return data;
    },
    enabled: Boolean(slug),
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      const { data } = await api.get<Category[]>("/products/categories");
      return data;
    },
  });
}

export function useRelatedProducts(categorySlug: string | undefined, excludeId: string | undefined) {
  return useQuery({
    queryKey: ["products", "related", categorySlug],
    queryFn: async () => {
      const { data } = await api.get<ProductListResponse>("/products", {
        params: { category: categorySlug, page_size: 5 },
      });
      return data;
    },
    enabled: Boolean(categorySlug),
    select: (data) => data.items.filter((item) => item.id !== excludeId).slice(0, 4),
  });
}
