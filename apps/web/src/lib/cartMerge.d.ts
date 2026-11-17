import type { CartItem } from "@/stores/cartStore";
import type { CustomerCartItem } from "@/types/commerce";

export function mergeCartItems(localItems: CartItem[], serverItems: CustomerCartItem[]): CartItem[];
export function mergeLocalCartItems(activeItems: CartItem[], cachedItems: CartItem[]): CartItem[];
