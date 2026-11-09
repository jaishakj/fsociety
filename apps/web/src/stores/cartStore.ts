import { create } from "zustand";
import { persist } from "zustand/middleware";

import { productUsesApparelSizes, type ProductSize } from "@/lib/productSizing";
import type { Category, Product } from "@/types/product";

export interface CartItem {
  id: string;
  productId: string;
  name: string;
  price: string;
  currency: string;
  image: string | null;
  quantity: number;
  categorySlug: string;
  categoryName: string;
  size: ProductSize | null;
}

type AddableProduct = Pick<Product, "id" | "name" | "price" | "currency" | "images"> & {
  category: Pick<Category, "slug" | "name">;
};

type PendingSizeSelection =
  | { kind: "add"; product: AddableProduct; quantity: number }
  | { kind: "update"; cartItemId: string; productName: string };

interface CartState {
  items: CartItem[];
  isOpen: boolean;
  pendingSizeSelection: PendingSizeSelection | null;
  addItem: (product: AddableProduct, quantity?: number, size?: ProductSize | null) => boolean;
  requestCartItemSize: (id: string) => void;
  choosePendingSize: (size: ProductSize) => void;
  closeSizePrompt: () => void;
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
      pendingSizeSelection: null,

      addItem: (product, quantity = 1, requestedSize = null) => {
        const hasSizes = productUsesApparelSizes(product.category.slug, product.category.name);
        const size = hasSizes ? requestedSize : null;

        if (hasSizes && !size) {
          set({ pendingSizeSelection: { kind: "add", product, quantity } });
          return false;
        }

        const productId = product.id;
        const lineId = size ? `${productId}:${size}` : productId;

        set((state) => {
          const existing = state.items.find((item) => item.id === lineId);

          if (existing) {
            return {
              items: state.items.map((item) =>
                item.id === lineId ? { ...item, quantity: item.quantity + quantity } : item,
              ),
              isOpen: true,
            };
          }

          return {
            items: [
              ...state.items,
              {
                id: lineId,
                productId,
                name: product.name,
                price: product.price,
                currency: product.currency,
                image: product.images[0]?.url ?? null,
                quantity,
                categorySlug: product.category.slug,
                categoryName: product.category.name,
                size,
              },
            ],
            isOpen: true,
          };
        });
        return true;
      },

      requestCartItemSize: (id) => {
        const item = get().items.find((cartItem) => cartItem.id === id);
        if (!item || !productUsesApparelSizes(item.categorySlug, item.categoryName) || item.size) return;
        set({ pendingSizeSelection: { kind: "update", cartItemId: item.id, productName: item.name } });
      },

      choosePendingSize: (size) => {
        const pending = get().pendingSizeSelection;
        if (!pending) return;

        if (pending.kind === "add") {
          const product = pending.product;
          const lineId = `${product.id}:${size}`;
          set((state) => {
            const existing = state.items.find((item) => item.id === lineId);

            if (existing) {
              return {
                items: state.items.map((item) =>
                  item.id === lineId ? { ...item, quantity: item.quantity + pending.quantity } : item,
                ),
                pendingSizeSelection: null,
                isOpen: true,
              };
            }

            return {
              items: [
                ...state.items,
                {
                  id: lineId,
                  productId: product.id,
                  name: product.name,
                  price: product.price,
                  currency: product.currency,
                  image: product.images[0]?.url ?? null,
                  quantity: pending.quantity,
                  categorySlug: product.category.slug,
                  categoryName: product.category.name,
                  size,
                },
              ],
              pendingSizeSelection: null,
              isOpen: true,
            };
          });
          return;
        }

        set((state) => {
          const selectedItem = state.items.find((item) => item.id === pending.cartItemId);
          if (!selectedItem) return { pendingSizeSelection: null };

          const lineId = `${selectedItem.productId}:${size}`;
          const existing = state.items.find((item) => item.id === lineId && item.id !== selectedItem.id);
          if (existing) {
            return {
              items: state.items
                .filter((item) => item.id !== selectedItem.id)
                .map((item) => item.id === lineId ? { ...item, quantity: item.quantity + selectedItem.quantity } : item),
              pendingSizeSelection: null,
            };
          }

          return {
            items: state.items.map((item) =>
              item.id === selectedItem.id ? { ...item, id: lineId, size } : item,
            ),
            pendingSizeSelection: null,
          };
        });
      },

      closeSizePrompt: () => set({ pendingSizeSelection: null }),

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
      version: 1,
      migrate: (persistedState) => {
        const oldState = persistedState as { items?: Array<Partial<CartItem> & { id: string; name: string }> };
        const items = Array.isArray(oldState.items) ? oldState.items : [];

        return {
          items: items.map((item) => ({
            ...item,
            productId: item.productId ?? item.id,
            categorySlug: item.categorySlug ?? "unknown",
            categoryName: item.categoryName ?? "",
            size: item.size ?? null,
          })),
        } as CartState;
      },
    },
  ),
);
