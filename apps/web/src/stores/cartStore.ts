import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { Product } from "@/types/product";

export interface CartItem {
  id: string;
  name: string;
  price: string;
  currency: string;
  image: string | null;
  quantity: number;
}

type AddableProduct = Pick<Product, "id" | "name" | "price" | "currency" | "images">

interface CartState {
  items: CartItem[];
  isOpen: boolean;
  addItem: (product: AddableProduct, quantity?: number) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  open: () => void;
  close: () => void;
  toggle: () => void;
  totalCount: () => number;
  totalPrice: () => number;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      isOpen: false,

      addItem: (product, quantity = 1) =>
        set((state) => {
          const existing = state.items.find((item) => item.id === product.id);

          if (existing) {
            return {
              items: state.items.map((item) =>
                item.id === product.id ? { ...item, quantity: item.quantity + quantity } : item,
              ),
              isOpen: true,
            };
          }

          return {
            items: [
              ...state.items,
              {
                id: product.id,
                name: product.name,
                price: product.price,
                currency: product.currency,
                image: product.images[0]?.url ?? null,
                quantity,
              },
            ],
            isOpen: true,
          };
        }),

      removeItem: (id) => set((state) => ({ items: state.items.filter((item) => item.id !== id) })),

      updateQuantity: (id, quantity) =>
        set((state) => ({
          items: state.items
            .map((item) => (item.id === id ? { ...item, quantity } : item))
            .filter((item) => item.quantity > 0),
        })),

      open: () => set({ isOpen: true }),
      close: () => set({ isOpen: false }),
      toggle: () => set((state) => ({ isOpen: !state.isOpen })),

      totalCount: () => get().items.reduce((sum, item) => sum + item.quantity, 0),
      totalPrice: () => get().items.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0),
    }),
    {
      name: "fsociety-cart",
      partialize: (state) => ({ items: state.items }),
    },
  ),
);
