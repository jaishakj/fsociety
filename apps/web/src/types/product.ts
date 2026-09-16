export interface ProductImage {
  id: string;
  url: string;
  alt: string | null;
  position: number;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  price: string;
  currency: string;
  stock: number;
  status: string;
  category: Category;
  images: ProductImage[];
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProductFilters {
  page?: number;
  category?: string;
  q?: string;
  min_price?: number;
  max_price?: number;
  sort?: "newest" | "price_asc" | "price_desc";
}
