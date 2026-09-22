import QRCode from "qrcode";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { useCartStore } from "@/stores/cartStore";

// ponytail: no payment gateway account/webhook exists, so there's no way to
// confirm a UPI payment actually landed. This page hands off to the buyer's
// UPI app and trusts them; upgrade path is a real gateway (Razorpay/Cashfree)
// with server-side webhook verification once real orders need confirming.
function buildUpiLink(amount: number, note: string): string | null {
  const vpa = import.meta.env.VITE_UPI_VPA;
  if (!vpa) return null;

  const params = new URLSearchParams({
    pa: vpa,
    pn: import.meta.env.VITE_UPI_PAYEE_NAME || "Fsociety",
    am: amount.toFixed(2),
    cu: "INR",
    tn: note,
  });
  return `upi://pay?${params.toString()}`;
}

export default function CheckoutPage() {
  const items = useCartStore((state) => state.items);
  const totalPrice = useCartStore((state) => state.totalPrice());
  const [qrDataUrl, setQrDataUrl] = useState<string | null>(null);

  const upiLink = items.length > 0 ? buildUpiLink(totalPrice, `Fsociety order, ${items.length} item(s)`) : null;

  useEffect(() => {
    if (!upiLink) {
      setQrDataUrl(null);
      return;
    }
    QRCode.toDataURL(upiLink, { margin: 1, width: 240 }).then(setQrDataUrl).catch(() => setQrDataUrl(null));
  }, [upiLink]);

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
            {items.map((item) => (
              <li key={item.id} className="flex items-center gap-4">
                {item.image ? (
                  <img src={item.image} alt={item.name} className="h-16 w-14 rounded-lg object-cover" />
                ) : (
                  <div className="h-16 w-14 rounded-lg bg-black/40" />
                )}
                <div className="flex-1">
                  <p className="text-sm text-[var(--color-paper)]">{item.name}</p>
                  <p className="font-mono text-xs text-[var(--color-steel)]">Qty {item.quantity}</p>
                </div>
                <span className="font-mono text-sm text-[var(--color-paper)]">
                  {item.currency} {(Number(item.price) * item.quantity).toFixed(2)}
                </span>
              </li>
            ))}
          </ul>
          <div className="mt-6 flex items-center justify-between border-t border-white/10 pt-4">
            <span className="text-[var(--color-paper)]">Total</span>
            <span className="font-mono text-lg text-[var(--color-signal)]">
              {items[0].currency} {totalPrice.toFixed(2)}
            </span>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-[var(--color-panel)] p-6 text-center">
          <h2 className="font-display text-lg text-[var(--color-paper)]">Pay with UPI</h2>

          {upiLink ? (
            <>
              <p className="font-mono mt-2 text-3xl text-[var(--color-paper)]">
                &#8377;{totalPrice.toFixed(2)}
              </p>

              {qrDataUrl ? (
                <img
                  src={qrDataUrl}
                  alt="Scan to pay with UPI"
                  className="mx-auto mt-6 h-[240px] w-[240px] rounded-2xl border border-white/10 bg-white p-3"
                />
              ) : (
                <div className="mx-auto mt-6 h-[240px] w-[240px] animate-pulse rounded-2xl bg-black/30" />
              )}

              <p className="font-mono mt-4 text-xs uppercase tracking-wide text-[var(--color-steel)]">
                Scan with any UPI app
              </p>

              <a href={upiLink} data-cursor className="mt-6 block">
                <Button variant="primary" className="w-full">
                  Open in UPI app
                </Button>
              </a>
              <p className="mt-3 text-xs text-[var(--color-steel)]">
                On desktop, scan the code instead, opening this link needs a UPI app on the same device.
              </p>
            </>
          ) : (
            <p className="mt-6 text-sm text-[var(--color-steel)]">
              Payment isn&apos;t configured yet. Please contact the store to complete this order.
            </p>
          )}
        </section>
      </div>
    </div>
  );
}
