import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { Product } from "@/types/product";

export interface WishlistItem {
  id: string;
  slug: string;
  name: string;
  price: string;
  currency: string;
  image: string | null;
}

interface WishlistState {
  items: WishlistItem[];
  toggle: (product: Product) => void;
  remove: (id: string) => void;
  has: (id: string) => boolean;
}

export const useWishlistStore = create<WishlistState>()(
  persist(
    (set, get) => ({
      items: [],

      toggle: (product) =>
        set((state) => {
          const exists = state.items.some((item) => item.id === product.id);
          if (exists) {
            return { items: state.items.filter((item) => item.id !== product.id) };
          }
          return {
            items: [
              ...state.items,
              {
                id: product.id,
                slug: product.slug,
                name: product.name,
                price: product.price,
                currency: product.currency,
                image: product.images[0]?.url ?? null,
              },
            ],
          };
        }),

      remove: (id) => set((state) => ({ items: state.items.filter((item) => item.id !== id) })),

      has: (id) => get().items.some((item) => item.id === id),
    }),
    { name: "fsociety-wishlist" },
  ),
);
