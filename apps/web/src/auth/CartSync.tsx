import { createContext, type ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";

import { useCustomerAuth } from "@/auth/customerAuth";
import { api, withAuth } from "@/lib/api";
import { mergeCartItems, mergeLocalCartItems } from "@/lib/cartMerge.js";
import { useCartStore, type CartItem } from "@/stores/cartStore";
import type { CustomerCart } from "@/types/commerce";

type CartSyncStatus = "idle" | "syncing" | "synced" | "error";

interface CartSyncValue {
  status: CartSyncStatus;
  error: string | null;
  ready: boolean;
  retry: () => void;
}

const CART_OWNER_KEY = "fsociety-cart-owner";
const USER_CART_CACHE_PREFIX = "fsociety-cart-account:";
const CartSyncContext = createContext<CartSyncValue | null>(null);

function accountCacheKey(userId: string) {
  return `${USER_CART_CACHE_PREFIX}${userId}`;
}

function readCartOwner(): string | null {
  try {
    return window.localStorage.getItem(CART_OWNER_KEY);
  } catch {
    return null;
  }
}

function writeCartOwner(userId: string) {
  try {
    window.localStorage.setItem(CART_OWNER_KEY, userId);
  } catch {
    // The API cart remains authoritative for signed-in users if storage is unavailable.
  }
}

function clearCartOwner() {
  try {
    window.localStorage.removeItem(CART_OWNER_KEY);
  } catch {
    // A stale owner marker is checked again on the next sign-in.
  }
}

function readAccountCache(userId: string): CartItem[] {
  try {
    const raw = window.localStorage.getItem(accountCacheKey(userId));
    if (!raw) return [];
    const value: unknown = JSON.parse(raw);
    if (!Array.isArray(value)) return [];
    return value.filter((item): item is CartItem =>
      typeof item?.id === "string" &&
      typeof item?.productId === "string" &&
      typeof item?.name === "string" &&
      typeof item?.price === "string" &&
      typeof item?.currency === "string" &&
      typeof item?.quantity === "number" &&
      Number.isInteger(item.quantity) &&
      item.quantity > 0 &&
      typeof item?.categorySlug === "string" &&
      typeof item?.categoryName === "string" &&
      (item?.size === null || ["XS", "S", "M", "L", "XL", "XXL"].includes(item?.size)) &&
      (item?.image === null || typeof item?.image === "string"),
    );
  } catch {
    return [];
  }
}

function writeAccountCache(userId: string, items: CartItem[]) {
  try {
    window.localStorage.setItem(accountCacheKey(userId), JSON.stringify(items));
  } catch {
    // Cart sync still works from the live store and API when browser storage is full.
  }
}

function clearAccountCache(userId: string) {
  try {
    window.localStorage.removeItem(accountCacheKey(userId));
  } catch {
    // A stale local cache is harmless; the next sync merges it with the user's API cart.
  }
}

function fingerprint(items: CartItem[]) {
  return JSON.stringify(items.map((item) => [
    item.id,
    item.productId,
    item.name,
    item.price,
    item.currency,
    item.image,
    item.quantity,
    item.categorySlug,
    item.categoryName,
    item.size,
  ]));
}

function toReplaceRequest(items: CartItem[]) {
  return {
    items: items.map((item) => ({
      product_id: item.productId,
      quantity: item.quantity,
      size: item.size,
    })),
  };
}

function unavailableMessage(error: unknown) {
  if (typeof error === "object" && error !== null && "response" in error) {
    const status = (error as { response?: { status?: number } }).response?.status;
    if (status === 401) return "Sign in again to save your bag to your account.";
    if (status === 409 || status === 422) {
      return "Some items are unavailable or exceed current stock. Adjust your bag; it is still saved on this device.";
    }
  }
  return "We couldn’t save your bag to your account. It is still saved on this device.";
}

export function CartSyncProvider({ children }: { children: ReactNode }) {
  const customerAuth = useCustomerAuth();
  const items = useCartStore((state) => state.items);
  const replaceItems = useCartStore((state) => state.replaceItems);
  const [status, setStatus] = useState<CartSyncStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [syncedUserId, setSyncedUserId] = useState<string | null>(null);
  const [retryVersion, setRetryVersion] = useState(0);
  const initializedUserId = useRef<string | null>(null);
  const lastSyncedFingerprint = useRef<string | null>(null);
  const consumedRetryVersion = useRef(0);
  const generation = useRef(0);
  const activeUserId = useRef<string | null>(customerAuth.userId);
  const saveQueue = useRef<Promise<void>>(Promise.resolve());
  activeUserId.current = customerAuth.userId;

  const retry = useCallback(() => setRetryVersion((value) => value + 1), []);

  useEffect(() => {
    const userId = customerAuth.userId;
    if (!customerAuth.configured || !customerAuth.isLoaded || !customerAuth.isSignedIn || !userId) {
      const previousOwner = readCartOwner();
      if (customerAuth.configured && customerAuth.isLoaded && !customerAuth.isSignedIn && previousOwner) {
        writeAccountCache(previousOwner, useCartStore.getState().items);
        replaceItems([]);
        clearCartOwner();
      }
      initializedUserId.current = null;
      setSyncedUserId(null);
      setStatus("idle");
      setError(null);
      return;
    }
    if (initializedUserId.current === userId) return;
    const authenticatedUserId = userId;

    const currentGeneration = ++generation.current;
    let cancelled = false;
    const isCurrent = () => !cancelled && generation.current === currentGeneration && activeUserId.current === authenticatedUserId;

    async function initializeCart() {
      setStatus("syncing");
      setError(null);
      try {
        let localItems = useCartStore.getState().items;
        const previousOwner = readCartOwner();
        if (previousOwner && previousOwner !== authenticatedUserId) {
          writeAccountCache(previousOwner, localItems);
          localItems = readAccountCache(authenticatedUserId);
          replaceItems(localItems);
        } else if (!previousOwner) {
          localItems = mergeLocalCartItems(localItems, readAccountCache(authenticatedUserId));
          replaceItems(localItems);
        }
        writeCartOwner(authenticatedUserId);

        const token = await customerAuth.getToken();
        if (!token) throw new Error("A signed-in session is required to sync the cart");
        const { data: serverCart } = await api.get<CustomerCart>("/cart", withAuth(token));
        if (!isCurrent()) return;

        const mergedItems = mergeCartItems(localItems, serverCart.items);
        replaceItems(mergedItems);
        const mergedFingerprint = fingerprint(mergedItems);
        initializedUserId.current = authenticatedUserId;

        if (serverCart.items.some((item) => !item.is_available)) {
          lastSyncedFingerprint.current = mergedFingerprint;
          setSyncedUserId(authenticatedUserId);
          setStatus("error");
          setError("Some saved items are no longer available or exceed stock. Remove or reduce them to sync your bag.");
          return;
        }

        try {
          const { data: savedCart } = await api.put<CustomerCart>("/cart", toReplaceRequest(mergedItems), withAuth(token));
          if (!isCurrent()) return;
          const canonicalItems = mergeCartItems([], savedCart.items);
          lastSyncedFingerprint.current = fingerprint(canonicalItems);
          if (fingerprint(useCartStore.getState().items) === mergedFingerprint) {
            replaceItems(canonicalItems);
          }
          writeCartOwner(authenticatedUserId);
          clearAccountCache(authenticatedUserId);
          setSyncedUserId(authenticatedUserId);
          setStatus("synced");
        } catch (syncError) {
          if (!isCurrent()) return;
          lastSyncedFingerprint.current = mergedFingerprint;
          setSyncedUserId(authenticatedUserId);
          setStatus("error");
          setError(unavailableMessage(syncError));
        }
      } catch (syncError) {
        if (!isCurrent()) return;
        setSyncedUserId(authenticatedUserId);
        setStatus("error");
        setError(unavailableMessage(syncError));
      }
    }

    void initializeCart();
    return () => {
      cancelled = true;
    };
  }, [
    customerAuth.configured,
    customerAuth.getToken,
    customerAuth.isLoaded,
    customerAuth.isSignedIn,
    customerAuth.userId,
    replaceItems,
    retryVersion,
  ]);

  useEffect(() => {
    const userId = customerAuth.userId;
    if (
      !customerAuth.configured ||
      !customerAuth.isLoaded ||
      !customerAuth.isSignedIn ||
      !userId ||
      initializedUserId.current !== userId
    ) return;

    const isManualRetry = retryVersion !== consumedRetryVersion.current;
    consumedRetryVersion.current = retryVersion;
    const currentFingerprint = fingerprint(items);
    if (currentFingerprint === lastSyncedFingerprint.current && !isManualRetry) return;

    const timeout = window.setTimeout(() => {
      setStatus("syncing");
      setError(null);
      saveQueue.current = saveQueue.current.catch(() => undefined).then(async () => {
        if (activeUserId.current !== userId) return;
        const latestItems = useCartStore.getState().items;
        const latestFingerprint = fingerprint(latestItems);
        if (latestFingerprint === lastSyncedFingerprint.current && !isManualRetry) {
          setStatus("synced");
          return;
        }
        try {
          const token = await customerAuth.getToken();
          if (!token) throw new Error("A signed-in session is required to sync the cart");
          const { data: savedCart } = await api.put<CustomerCart>("/cart", toReplaceRequest(latestItems), withAuth(token));
          if (activeUserId.current !== userId) return;
          const canonicalItems = mergeCartItems([], savedCart.items);
          lastSyncedFingerprint.current = fingerprint(canonicalItems);
          if (fingerprint(useCartStore.getState().items) === latestFingerprint) {
            replaceItems(canonicalItems);
          }
          writeCartOwner(userId);
          clearAccountCache(userId);
          setSyncedUserId(userId);
          setStatus("synced");
        } catch (syncError) {
          if (activeUserId.current !== userId) return;
          lastSyncedFingerprint.current = fingerprint(useCartStore.getState().items);
          setSyncedUserId(userId);
          setStatus("error");
          setError(unavailableMessage(syncError));
        }
      });
    }, 350);

    return () => window.clearTimeout(timeout);
  }, [
    customerAuth.configured,
    customerAuth.getToken,
    customerAuth.isLoaded,
    customerAuth.isSignedIn,
    customerAuth.userId,
    items,
    replaceItems,
    retryVersion,
  ]);

  const ready = !customerAuth.configured || (
    customerAuth.isLoaded &&
    (!customerAuth.isSignedIn || syncedUserId === customerAuth.userId)
  );

  return (
    <CartSyncContext.Provider value={{ status, error, ready, retry }}>
      {children}
    </CartSyncContext.Provider>
  );
}

export function useCartSyncStatus() {
  const value = useContext(CartSyncContext);
  if (!value) throw new Error("useCartSyncStatus must be used inside CartSyncProvider");
  return value;
}
