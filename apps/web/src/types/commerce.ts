export interface CartMerchandiseQuoteLine {
  product_id: string;
  name: string;
  quantity: number;
  size: "XS" | "S" | "M" | "L" | "XL" | "XXL" | null;
  unit_price: string;
  line_subtotal: string;
}

export interface CartMerchandiseQuote {
  currency: string;
  items: CartMerchandiseQuoteLine[];
  merchandise_subtotal: string;
}

export interface CustomerCartItem {
  id: string;
  product_id: string;
  name: string;
  slug: string;
  category_slug: string;
  category_name: string;
  quantity: number;
  size: "XS" | "S" | "M" | "L" | "XL" | "XXL" | null;
  unit_price: string;
  currency: string;
  image_url: string | null;
  is_available: boolean;
}

export interface CustomerCart {
  cart_id: string | null;
  updated_at: string | null;
  items: CustomerCartItem[];
}
