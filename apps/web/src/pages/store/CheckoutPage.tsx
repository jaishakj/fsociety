import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";

import { useCustomerAuth } from "@/auth/customerAuth";
import { getShippingProfile } from "@/auth/shippingProfile";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { productUsesApparelSizes } from "@/lib/productSizing";
import { useCartStore } from "@/stores/cartStore";
import type { CartMerchandiseQuote } from "@/types/commerce";

export default function CheckoutPage() {
  const items = useCartStore((state) => state.items);
  const requestCartItemSize = useCartStore((state) => state.requestCartItemSize);
  const customerAuth = useCustomerAuth();
  const [shippingReady, setShippingReady] = useState(false);
  const [shippingError, setShippingError] = useState(false);
  const [shippingMissing, setShippingMissing] = useState(false);
  const quoteItems = items.map((item) => ({ product_id: item.productId, quantity: item.quantity }));
  const itemMissingSize = items.find((item) =>
    productUsesApparelSizes(item.categorySlug, item.categoryName) && !item.size,
  );
  const quoteQuery = useQuery({
    queryKey: ["cart-merchandise-quote", quoteItems],
    queryFn: async () => {
      const { data } = await api.post<CartMerchandiseQuote>("/cart/merchandise-quote", { items: quoteItems });
      if (
        data.items.length !== quoteItems.length ||
        data.items.some((line, index) =>
          line.product_id !== quoteItems[index].product_id || line.quantity !== quoteItems[index].quantity,
        )
      ) {
        throw new Error("The price response did not match the saved bag");
      }
      return data;
    },
    enabled:
      items.length > 0 &&
      !itemMissingSize &&
      (!customerAuth.configured || (customerAuth.isLoaded && customerAuth.isSignedIn && shippingReady)),
    retry: 1,
  });

  useEffect(() => {
    if (itemMissingSize) requestCartItemSize(itemMissingSize.id);
  }, [itemMissingSize, requestCartItemSize]);

  useEffect(() => {
    let active = true;
    if (!customerAuth.configured || !customerAuth.isLoaded || !customerAuth.isSignedIn || items.length === 0) {
      setShippingReady(false);
      setShippingError(false);
      setShippingMissing(false);
      return () => { active = false; };
    }
    setShippingError(false);
    setShippingMissing(false);
    customerAuth.getToken().then(async (token) => {
      if (!token) throw new Error("Missing customer session");
      await getShippingProfile(token);
      if (active) setShippingReady(true);
    }).catch((error: unknown) => {
      if (!active) return;
      const status = typeof error === "object" && error !== null && "response" in error
        ? (error as { response?: { status?: number } }).response?.status
        : undefined;
      setShippingError(status !== 404);
      setShippingMissing(status === 404);
      setShippingReady(false);
    });
    return () => { active = false; };
  }, [customerAuth, items.length]);

  if (items.length === 0) {
    return (
      <div className="py-24 text-center">
        <p className="text-[var(--color-steel)]">Your bag is empty.</p>
        <Link to="/shop" data-cursor className="mt-4 inline-block text-[var(--color-signal)] underline">
          Back to shop
        </Link>
      </div>
    );
  }

  if (itemMissingSize) {
    return (
      <div className="py-24 text-center">
        <p className="font-display text-2xl text-[var(--color-paper)]">Choose your sizes first</p>
        <p className="mt-3 text-sm text-[var(--color-steel)]">Select a size for each clothing item to continue to payment.</p>
        <Link to="/shop" data-cursor className="mt-5 inline-block text-[var(--color-signal)] underline">
          Continue shopping
        </Link>
      </div>
    );
  }

  if (customerAuth.configured) {
    if (!customerAuth.isLoaded) return <p className="py-24 text-center text-sm text-[var(--color-steel)]">Checking your account…</p>;
    if (!customerAuth.isSignedIn) return (
      <section className="mx-auto max-w-xl py-24 text-center">
        <h1 className="font-display text-3xl text-[var(--color-paper)]">Sign in to continue</h1>
        <p className="mt-3 text-sm text-[var(--color-steel)]">Your shipping details are saved securely to your account.</p>
        <Link to="/sign-in" onClick={() => window.sessionStorage.setItem("fsociety.checkout-after-signin", "1")} className="mt-6 inline-flex min-h-12 items-center rounded-full bg-[var(--color-signal)] px-6 text-sm font-medium text-[var(--color-void)]">Sign in</Link>
        <p className="mt-4 text-sm text-[var(--color-steel)]">New here? <Link to="/sign-up" className="text-[var(--color-paper)] underline">Create an account</Link></p>
      </section>
    );
    if (shippingError) return <section className="mx-auto max-w-xl py-24 text-center"><h1 className="font-display text-3xl text-[var(--color-paper)]">Couldn’t verify delivery details</h1><p className="mt-3 text-sm text-[var(--color-steel)]">Please refresh or sign in again before checkout.</p><Link to="/account" className="mt-6 inline-flex min-h-12 items-center rounded-full border border-white/15 px-6 text-sm text-[var(--color-paper)]">Go to account</Link></section>;
    if (shippingMissing) return <Navigate to="/account/setup" replace />;
    if (!shippingReady) return <p className="py-24 text-center text-sm text-[var(--color-steel)]">Checking your shipping details…</p>;
  }

  return (
    <div className="relative py-10 pb-24">
      <div
        className="pointer-events-none absolute -top-20 left-1/4 h-[420px] w-[420px] rounded-full blur-3xl"
        style={{ background: "var(--color-signal-dim)", opacity: 0.35 }}
      />
      <div
        className="pointer-events-none absolute right-1/4 top-1/2 h-[320px] w-[320px] rounded-full blur-3xl"
        style={{ background: "var(--color-signal-dim)", opacity: 0.25 }}
      />

      <h1 className="relative z-10 font-display text-4xl text-[var(--color-paper)]">Checkout</h1>

      <div className="relative z-10 mt-10 grid grid-cols-1 gap-10 md:grid-cols-[1.2fr_1fr]">
        <section className="rounded-3xl border border-white/10 bg-[var(--color-panel)] p-6">
          <h2 className="font-display text-lg text-[var(--color-paper)]">Order summary</h2>
          <ul className="mt-6 space-y-4">
            {items.map((item, index) => {
              const quotedItem = quoteQuery.data?.items[index];
              return (
                <li key={item.id} className="flex items-center gap-4">
                  {item.image ? (
                    <img src={item.image} alt={item.name} className="h-16 w-14 rounded-lg object-cover" />
                  ) : (
                    <div className="h-16 w-14 rounded-lg bg-black/40" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm text-[var(--color-paper)]">{quotedItem?.name ?? item.name}</p>
                    <p className="text-xs text-[var(--color-steel)]">Qty {item.quantity}</p>
                    {item.size ? <p className="text-xs text-[var(--color-steel)]">Size {item.size}</p> : null}
                  </div>
                  <span className="font-mono text-sm text-[var(--color-paper)]">
                    {quotedItem
                      ? `${quoteQuery.data?.currency} ${quotedItem.line_subtotal}`
                      : quoteQuery.isError
                        ? "Price unavailable"
                        : "Checking price…"}
                  </span>
                </li>
              );
            })}
          </ul>
          {quoteQuery.data ? (
            <div role="status" className="mt-6 flex items-center justify-between border-t border-white/10 pt-4">
              <span className="text-[var(--color-paper)]">Merchandise subtotal</span>
              <span className="font-mono text-lg text-[var(--color-signal)]">
                {quoteQuery.data.currency} {quoteQuery.data.merchandise_subtotal}
              </span>
            </div>
          ) : quoteQuery.isError ? (
            <div className="mt-6 border-t border-white/10 pt-4 text-left">
              <p role="status" className="text-sm text-[var(--color-signal)]">
                We couldn&apos;t verify current prices or availability. Your saved bag has not been changed.
              </p>
              <Button
                type="button"
                variant="outline"
                className="mt-4 w-full"
                onClick={() => void quoteQuery.refetch()}
              >
                Retry price check
              </Button>
            </div>
          ) : (
            <p className="mt-6 border-t border-white/10 pt-4 text-sm text-[var(--color-steel)]">
              Checking current product prices&hellip;
            </p>
          )}
        </section>

        <section aria-labelledby="checkout-payment-heading" className="rounded-3xl border border-white/10 bg-[var(--color-panel)] p-6 text-center">
          <h2 id="checkout-payment-heading" className="font-display text-lg text-[var(--color-paper)]">
            Payment unavailable
          </h2>
          <p className="mt-3 text-sm leading-6 text-[var(--color-steel)]">
            Secure online payment is not configured yet. No order has been placed and no payment has been taken.
            Your bag is saved so you can come back later.
          </p>
          <Link to="/shop" data-cursor className="mt-6 inline-flex min-h-12 items-center justify-center rounded-full border border-white/15 px-6 text-sm text-[var(--color-paper)] transition-colors hover:bg-white/5">
            Continue shopping
          </Link>
        </section>
      </div>
    </div>
  );
}
