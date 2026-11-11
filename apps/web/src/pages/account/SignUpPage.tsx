import { SignUp } from "@clerk/react";
import { Link } from "react-router-dom";

import { useCustomerAuth } from "@/auth/customerAuth";

export default function SignUpPage() {
  const auth = useCustomerAuth();
  return (
    <section className="mx-auto max-w-xl py-12 sm:py-20">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">FSOCIETY / ACCOUNT</p>
      <h1 className="mt-3 font-display text-4xl text-[var(--color-paper)]">Make it yours.</h1>
      <p className="mt-3 max-w-md text-sm leading-6 text-[var(--color-steel)]">Create an account with your email. We’ll ask for your shipping phone and address right after verification.</p>
      {!auth.configured ? (
        <div className="mt-8 rounded-2xl border border-white/10 bg-[var(--color-panel)] p-6 text-sm text-[var(--color-steel)]">
          Customer sign-up is being configured. The site owner needs to add <code className="font-mono text-[var(--color-paper)]">VITE_CLERK_PUBLISHABLE_KEY</code> to the web app’s environment.
        </div>
      ) : (
        <div className="mt-8 flex justify-center rounded-3xl border border-white/10 bg-[var(--color-panel)] p-4 sm:p-8">
          <SignUp routing="hash" forceRedirectUrl="/account/setup" signInUrl="/sign-in" />
        </div>
      )}
      <p className="mt-6 text-sm text-[var(--color-steel)]">Already a member? <Link className="text-[var(--color-paper)] underline underline-offset-4" to="/sign-in">Sign in</Link></p>
    </section>
  );
}
