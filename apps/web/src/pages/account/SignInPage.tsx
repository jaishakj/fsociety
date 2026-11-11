import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useCustomerAuth } from "@/auth/customerAuth";
import { Button } from "@/components/ui/Button";

function loginError(error: unknown) {
  const response = typeof error === "object" && error !== null && "response" in error
    ? (error as { response?: { data?: { detail?: unknown } } }).response
    : undefined;
  if (response?.data?.detail === "Incorrect email or password") return "We couldn’t match that email and password. Check them and try again.";
  if (typeof response?.data?.detail === "string") return response.data.detail;
  return "We couldn’t sign you in. Please try again.";
}

export default function SignInPage() {
  const auth = useCustomerAuth();
  const navigate = useNavigate();
  const redirectAfterSignIn = window.sessionStorage.getItem("fsociety.checkout-after-signin") === "1"
    ? "/checkout"
    : "/account";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      await auth.signIn(email, password);
      navigate(redirectAfterSignIn, { replace: true });
    } catch (reason) {
      setError(loginError(reason));
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="mx-auto max-w-xl py-12 sm:py-20">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">FSOCIETY / ACCOUNT</p>
      <h1 className="mt-3 font-display text-4xl text-[var(--color-paper)]">Welcome back.</h1>
      <p className="mt-3 max-w-md text-sm leading-6 text-[var(--color-steel)]">Sign in securely to manage your shipping details and continue to checkout.</p>
      <form onSubmit={submit} className="mt-8 grid gap-5 rounded-3xl border border-white/10 bg-[var(--color-panel)] p-5 sm:p-8">
        <label className="grid gap-2 text-sm text-[var(--color-steel)]">
          Email address
          <input required type="email" autoComplete="email" maxLength={255} value={email} onChange={(event) => setEmail(event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" />
        </label>
        <label className="grid gap-2 text-sm text-[var(--color-steel)]">
          Password
          <input required type="password" autoComplete="current-password" maxLength={128} value={password} onChange={(event) => setPassword(event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" />
        </label>
        {error ? <p role="alert" className="text-sm text-[var(--color-signal)]">{error}</p> : null}
        <Button type="submit" disabled={saving || !auth.isLoaded} className="w-full">{saving ? "Signing in…" : "Sign in"}</Button>
      </form>
      <p className="mt-6 text-sm text-[var(--color-steel)]">New here? <Link className="text-[var(--color-paper)] underline underline-offset-4" to="/sign-up">Create an account</Link></p>
    </section>
  );
}
