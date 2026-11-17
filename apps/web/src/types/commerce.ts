export interface CartMerchandiseQuoteLine {
  product_id: string;
  name: string;
  quantity: number;
  unit_price: string;
  line_subtotal: string;
}

export interface CartMerchandiseQuote {
  currency: string;
  items: CartMerchandiseQuoteLine[];
  merchandise_subtotal: string;
}
