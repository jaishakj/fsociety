import { SignIn } from "@clerk/react";
import { Link } from "react-router-dom";

import { useCustomerAuth } from "@/auth/customerAuth";

export default function SignInPage() {
  const auth = useCustomerAuth();
  const redirectAfterSignIn = window.sessionStorage.getItem("fsociety.checkout-after-signin") === "1"
    ? "/checkout"
    : "/account";
  return (
    <section className="mx-auto max-w-xl py-12 sm:py-20">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">FSOCIETY / ACCOUNT</p>
      <h1 className="mt-3 font-display text-4xl text-[var(--color-paper)]">Welcome back.</h1>
      <p className="mt-3 max-w-md text-sm leading-6 text-[var(--color-steel)]">Sign in securely to manage your shipping details and continue to checkout.</p>
      {!auth.configured ? (
        <div className="mt-8 rounded-2xl border border-white/10 bg-[var(--color-panel)] p-6 text-sm text-[var(--color-steel)]">
          Customer sign-in is being configured. Please try again soon.
        </div>
      ) : (
        <div className="mt-8 flex justify-center rounded-3xl border border-white/10 bg-[var(--color-panel)] p-4 sm:p-8">
          <SignIn routing="hash" forceRedirectUrl={redirectAfterSignIn} signUpUrl="/sign-up" />
        </div>
      )}
      <p className="mt-6 text-sm text-[var(--color-steel)]">New here? <Link className="text-[var(--color-paper)] underline underline-offset-4" to="/sign-up">Create an account</Link></p>
    </section>
  );
}
