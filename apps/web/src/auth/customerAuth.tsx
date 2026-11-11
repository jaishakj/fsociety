import { ClerkProvider, useAuth, useClerk, useUser } from "@clerk/react";
import { createContext, type ReactNode, useContext, useMemo } from "react";

type CustomerAuthValue = {
  configured: boolean;
  isLoaded: boolean;
  isSignedIn: boolean;
  userId: string | null;
  email: string | null;
  getToken: () => Promise<string | null>;
  signOut: () => Promise<void>;
};

const unavailableAuth: CustomerAuthValue = {
  configured: false,
  isLoaded: true,
  isSignedIn: false,
  userId: null,
  email: null,
  getToken: async () => null,
  signOut: async () => undefined,
};

const CustomerAuthContext = createContext<CustomerAuthValue>(unavailableAuth);

function ClerkCustomerAuth({ children }: { children: ReactNode }) {
  const { isLoaded, isSignedIn, userId, getToken } = useAuth();
  const { user } = useUser();
  const { signOut } = useClerk();
  const value = useMemo<CustomerAuthValue>(() => ({
    configured: true,
    isLoaded,
    isSignedIn: Boolean(isSignedIn),
    userId: userId ?? null,
    email: user?.primaryEmailAddress?.emailAddress ?? null,
    getToken: () => getToken(),
    signOut: () => signOut(),
  }), [getToken, isLoaded, isSignedIn, signOut, user?.primaryEmailAddress?.emailAddress, userId]);

  return <CustomerAuthContext.Provider value={value}>{children}</CustomerAuthContext.Provider>;
}

const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY?.trim();

export function CustomerAuthProvider({ children }: { children: ReactNode }) {
  if (!publishableKey) {
    return <CustomerAuthContext.Provider value={unavailableAuth}>{children}</CustomerAuthContext.Provider>;
  }

  return (
    <ClerkProvider
      publishableKey={publishableKey}
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      signInFallbackRedirectUrl="/account/setup"
      signUpFallbackRedirectUrl="/account/setup"
    >
      <ClerkCustomerAuth>{children}</ClerkCustomerAuth>
    </ClerkProvider>
  );
}

export function useCustomerAuth() {
  return useContext(CustomerAuthContext);
}
