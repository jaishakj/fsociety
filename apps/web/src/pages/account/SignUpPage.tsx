import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useCustomerAuth } from "@/auth/customerAuth";
import { Button } from "@/components/ui/Button";

function registrationError(error: unknown) {
  const response = typeof error === "object" && error !== null && "response" in error
    ? (error as { response?: { data?: { detail?: unknown } } }).response
    : undefined;
  if (typeof response?.data?.detail === "string") return response.data.detail;
  if (Array.isArray(response?.data?.detail)) return "Enter a valid email and a password with at least 12 characters.";
  return error instanceof Error ? error.message : "We couldn’t create your account. Please try again.";
}

export default function SignUpPage() {
  const auth = useCustomerAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }
    setSaving(true);
    try {
      await auth.signUp(email, password);
      navigate("/account/setup", { replace: true });
    } catch (reason) {
      setError(registrationError(reason));
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="mx-auto max-w-xl py-12 sm:py-20">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">FSOCIETY / ACCOUNT</p>
      <h1 className="mt-3 font-display text-4xl text-[var(--color-paper)]">Make it yours.</h1>
      <p className="mt-3 max-w-md text-sm leading-6 text-[var(--color-steel)]">Create your account with email and password. Add your shipping phone and address in the next step.</p>
      <form onSubmit={submit} className="mt-8 grid gap-5 rounded-3xl border border-white/10 bg-[var(--color-panel)] p-5 sm:p-8">
        <label className="grid gap-2 text-sm text-[var(--color-steel)]">
          Email address
          <input required type="email" autoComplete="email" maxLength={255} value={email} onChange={(event) => setEmail(event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" />
        </label>
        <label className="grid gap-2 text-sm text-[var(--color-steel)]">
          Password
          <input required type="password" autoComplete="new-password" minLength={12} maxLength={128} value={password} onChange={(event) => setPassword(event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" />
          <span className="text-xs">Use at least 12 characters.</span>
        </label>
        <label className="grid gap-2 text-sm text-[var(--color-steel)]">
          Confirm password
          <input required type="password" autoComplete="new-password" minLength={12} maxLength={128} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} className="min-h-12 rounded-xl border border-white/10 bg-[var(--color-void)] px-4 text-[var(--color-paper)] outline-none focus:border-[var(--color-signal)]" />
        </label>
        {error ? <p role="alert" className="text-sm text-[var(--color-signal)]">{error}</p> : null}
        <Button type="submit" disabled={saving || !auth.isLoaded} className="w-full">{saving ? "Creating account…" : "Create account"}</Button>
        <p className="text-xs leading-5 text-[var(--color-steel)]">Your password is stored as a one-way Argon2 hash. Your shipping details are stored separately in the store database.</p>
      </form>
      <p className="mt-6 text-sm text-[var(--color-steel)]">Already a member? <Link className="text-[var(--color-paper)] underline underline-offset-4" to="/sign-in">Sign in</Link></p>
    </section>
  );
}
