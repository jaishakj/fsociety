import { useEffect, useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { useCustomerAuth } from "@/auth/customerAuth";
import { getShippingProfile, saveShippingProfile, type ShippingProfile } from "@/auth/shippingProfile";
import { Button } from "@/components/ui/Button";

const emptyProfile: ShippingProfile = {
  phone_number: "",
  address_line_1: "",
  address_line_2: "",
  city: "",
  state_or_region: "",
  postal_code: "",
  country: "India",
};

export default function ShippingProfilePage() {
  const auth = useCustomerAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(emptyProfile);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    if (!auth.isLoaded || !auth.isSignedIn) return () => { active = false; };
    auth.getToken().then(async (token) => {
      if (!token) {
        if (active) { setError("Your session needs to refresh. Please sign in again."); setLoading(false); }
        return;
      }
      try {
        const existing = await getShippingProfile(token);
        if (active) setProfile(existing);
      } catch (reason) {
        if (active && !(reason instanceof Error && "response" in reason && (reason as { response?: { status?: number } }).response?.status === 404)) {
          setError("We couldn’t load your saved address. Please try again.");
        }
      } finally {
        if (active) setLoading(false);
      }
    }).catch(() => {
      if (active) { setError("Your session needs to refresh. Please sign in again."); setLoading(false); }
    });
    return () => { active = false; };
  }, [auth]);

  if (auth.isLoaded && !auth.isSignedIn) return <Navigate to="/sign-in" replace />;
  if (!auth.configured) return <Navigate to="/sign-up" replace />;

  const update = (key: keyof ShippingProfile, value: string) => setProfile((current) => ({ ...current, [key]: value }));
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      const token = await auth.getToken();
      if (!token) throw new Error("Sign in again to save your shipping address.");
      await saveShippingProfile(token, { ...profile, address_line_2: profile.address_line_2?.trim() || null });
      const returnToCheckout = window.sessionStorage.getItem("fsociety.checkout-after-signin") === "1";
      window.sessionStorage.removeItem("fsociety.checkout-after-signin");
      navigate(returnToCheckout ? "/checkout" : "/account", { replace: true });
    } catch (reason) {
      setError(reason instanceof Error && !("response" in reason) ? reason.message : "We couldn’t save your details. Please check your connection and try again.");
    } finally {
      setSaving(false);
    }
  }

  if (!auth.isLoaded || loading) return <p className="py-24 text-center text-sm text-[var(--color-steel)]">Loading your account…</p>;

  return (
    <section className="mx-auto max-w-2xl py-10 sm:py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">DELIVERY DETAILS</p>
      <h1 className="mt-3 font-display text-4xl text-[var(--color-paper)]">Where should it go?</h1>
      <p className="mt-3 text-sm leading-6 text-[var(--color-steel)]">Add your phone number and shipping address to finish setting up your account. Only you and authorized store administrators can access these details.</p>
      <form onSubmit={submit} className="mt-8 grid gap-5 rounded-3xl border border-white/10 bg-[var(--color-panel)] p-5 sm:grid-cols-2 sm:p-8">
        <label className="grid gap-2 text-sm text-[var(--color-steel)] sm:col-span-2">Mobile number<input required autoComplete="tel" type="tel" inputMode="tel" minLength={7} maxLength={32} value={profile.phone_number} onChange={(event) => update("phone_number", event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" /></label>
        <label className="grid gap-2 text-sm text-[var(--color-steel)] sm:col-span-2">Address line 1<input required autoComplete="address-line1" maxLength={200} value={profile.address_line_1} onChange={(event) => update("address_line_1", event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" /></label>
        <label className="grid gap-2 text-sm text-[var(--color-steel)] sm:col-span-2">Apartment, suite, landmark <span className="text-xs">Optional</span><input autoComplete="address-line2" maxLength={200} value={profile.address_line_2 ?? ""} onChange={(event) => update("address_line_2", event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" /></label>
        <label className="grid gap-2 text-sm text-[var(--color-steel)]">City / town<input required autoComplete="address-level2" maxLength={100} value={profile.city} onChange={(event) => update("city", event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" /></label>
        <label className="grid gap-2 text-sm text-[var(--color-steel)]">State / region<input required autoComplete="address-level1" maxLength={100} value={profile.state_or_region} onChange={(event) => update("state_or_region", event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" /></label>
        <label className="grid gap-2 text-sm text-[var(--color-steel)]">Postal code<input required autoComplete="postal-code" maxLength={24} value={profile.postal_code} onChange={(event) => update("postal_code", event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" /></label>
        <label className="grid gap-2 text-sm text-[var(--color-steel)]">Country<input required autoComplete="country-name" maxLength={100} value={profile.country} onChange={(event) => update("country", event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" /></label>
        {error ? <p role="alert" className="text-sm text-[var(--color-signal)] sm:col-span-2">{error}</p> : null}
        <div className="flex flex-col gap-3 sm:col-span-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs leading-5 text-[var(--color-steel)]">Your address is stored with the store database, not in public profile metadata.</p>
          <Button type="submit" disabled={saving} className="w-full sm:w-auto">{saving ? "Saving…" : "Save and continue"}</Button>
        </div>
      </form>
    </section>
  );
}
