import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";

import { useCustomerAuth } from "@/auth/customerAuth";
import { getShippingProfile, type ShippingProfile } from "@/auth/shippingProfile";
import { Button } from "@/components/ui/Button";

export default function AccountPage() {
  const auth = useCustomerAuth();
  const [profile, setProfile] = useState<ShippingProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    if (!auth.isLoaded || !auth.isSignedIn) return () => { active = false; };
    auth.getToken().then(async (token) => {
      if (!token) {
        if (active) setLoading(false);
        return;
      }
      try { const result = await getShippingProfile(token); if (active) setProfile(result); }
      catch { if (active) setProfile(null); }
      finally { if (active) setLoading(false); }
    }).catch(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [auth]);

  if (auth.isLoaded && !auth.isSignedIn) return <Navigate to="/sign-in" replace />;
  if (!auth.configured) return <Navigate to="/sign-up" replace />;
  if (!auth.isLoaded || loading) return <p className="py-24 text-center text-sm text-[var(--color-steel)]">Loading your account…</p>;
  if (!profile) return <Navigate to="/account/setup" replace />;

  return (
    <section className="mx-auto max-w-3xl py-10 sm:py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">YOUR FSOCIETY</p>
      <h1 className="mt-3 font-display text-4xl text-[var(--color-paper)]">Account</h1>
      <div className="mt-8 rounded-3xl border border-white/10 bg-[var(--color-panel)] p-6 sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div><h2 className="font-display text-xl text-[var(--color-paper)]">Shipping details</h2><p className="mt-1 text-sm text-[var(--color-steel)]">Used to prepare your delivery.</p></div>
          <Link to="/account/setup" className="text-sm text-[var(--color-paper)] underline underline-offset-4">Edit details</Link>
        </div>
        <dl className="mt-6 grid gap-4 text-sm sm:grid-cols-2">
          <div><dt className="text-[var(--color-steel)]">Account email</dt><dd className="mt-1 text-[var(--color-paper)]">{auth.email ?? "Signed in"}</dd></div>
          <div><dt className="text-[var(--color-steel)]">Mobile</dt><dd className="mt-1 text-[var(--color-paper)]">{profile.phone_number}</dd></div>
          <div className="sm:col-span-2"><dt className="text-[var(--color-steel)]">Delivery address</dt><dd className="mt-1 leading-6 text-[var(--color-paper)]">{[profile.address_line_1, profile.address_line_2, profile.city, profile.state_or_region, profile.postal_code, profile.country].filter(Boolean).join(", ")}</dd></div>
        </dl>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/shop" className="inline-flex min-h-12 items-center rounded-full border border-white/15 px-5 text-sm text-[var(--color-paper)]">Continue shopping</Link>
          <Button variant="outline" onClick={() => void auth.signOut()}>Sign out</Button>
        </div>
      </div>
    </section>
  );
}
