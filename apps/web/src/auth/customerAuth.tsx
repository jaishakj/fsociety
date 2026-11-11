import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";

import { api, withAuth } from "@/lib/api";

type CustomerUser = {
  id: string;
  email: string;
  display_name: string | null;
  roles: string[];
};

type TokenPair = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: "bearer";
};

type StoredSession = TokenPair & { expires_at: number };

type CustomerAuthValue = {
  configured: boolean;
  isLoaded: boolean;
  isSignedIn: boolean;
  userId: string | null;
  email: string | null;
  getToken: () => Promise<string | null>;
  signUp: (email: string, password: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const SESSION_KEY = "fsociety.customer.session.v1";
const EXPIRY_SKEW_MS = 30_000;

function readSession(): StoredSession | null {
  try {
    const raw = window.sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const value = JSON.parse(raw) as Partial<StoredSession>;
    if (
      typeof value.access_token !== "string" ||
      typeof value.refresh_token !== "string" ||
      typeof value.expires_at !== "number"
    ) return null;
    return value as StoredSession;
  } catch {
    return null;
  }
}

function persistSession(tokens: TokenPair): StoredSession {
  const session = { ...tokens, expires_at: Date.now() + tokens.expires_in * 1000 };
  window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
}

function clearStoredSession() {
  window.sessionStorage.removeItem(SESSION_KEY);
}

const CustomerAuthContext = createContext<CustomerAuthValue | null>(null);

export function CustomerAuthProvider({ children }: { children: ReactNode }) {
  const sessionRef = useRef<StoredSession | null>(readSession());
  const refreshRef = useRef<Promise<string | null> | null>(null);
  const [user, setUser] = useState<CustomerUser | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  const getToken = useCallback(async (): Promise<string | null> => {
    const session = sessionRef.current ?? readSession();
    if (!session) return null;
    if (session.expires_at > Date.now() + EXPIRY_SKEW_MS) {
      sessionRef.current = session;
      return session.access_token;
    }
    if (!session.refresh_token) {
      sessionRef.current = null;
      clearStoredSession();
      setUser(null);
      return null;
    }

    if (!refreshRef.current) {
      refreshRef.current = api.post<TokenPair>("/auth/refresh", {
        refresh_token: session.refresh_token,
      }).then((response) => {
        const refreshed = persistSession(response.data);
        sessionRef.current = refreshed;
        return refreshed.access_token;
      }).catch(() => {
        sessionRef.current = null;
        clearStoredSession();
        setUser(null);
        return null;
      }).finally(() => {
        refreshRef.current = null;
      });
    }
    return refreshRef.current;
  }, []);

  const loadCurrentUser = useCallback(async (token: string) => {
    const response = await api.get<CustomerUser>("/auth/me", withAuth(token));
    setUser(response.data);
  }, []);

  useEffect(() => {
    let active = true;
    async function bootstrap() {
      const session = readSession();
      sessionRef.current = session;
      if (!session) {
        if (active) setIsLoaded(true);
        return;
      }
      const token = await getToken();
      if (token) {
        try {
          const response = await api.get<CustomerUser>("/auth/me", withAuth(token));
          if (active) setUser(response.data);
        } catch {
          sessionRef.current = null;
          clearStoredSession();
          if (active) setUser(null);
        }
      }
      if (active) setIsLoaded(true);
    }
    void bootstrap();
    return () => { active = false; };
  }, [getToken]);

  const signIn = useCallback(async (email: string, password: string) => {
    const normalizedEmail = email.trim().toLowerCase();
    const response = await api.post<TokenPair>("/auth/login", { email: normalizedEmail, password });
    sessionRef.current = persistSession(response.data);
    await loadCurrentUser(response.data.access_token);
  }, [loadCurrentUser]);

  const signUp = useCallback(async (email: string, password: string) => {
    const normalizedEmail = email.trim().toLowerCase();
    const registered = await api.post<CustomerUser>("/auth/register", { email: normalizedEmail, password });
    try {
      const response = await api.post<TokenPair>("/auth/login", { email: normalizedEmail, password });
      sessionRef.current = persistSession(response.data);
      setUser(registered.data);
    } catch {
      throw new Error("Your account was created. Please sign in to continue.");
    }
  }, []);

  const signOut = useCallback(async () => {
    const token = await getToken();
    try {
      if (token) await api.post("/auth/logout", undefined, withAuth(token));
    } finally {
      sessionRef.current = null;
      clearStoredSession();
      setUser(null);
    }
  }, [getToken]);

  const value = useMemo<CustomerAuthValue>(() => ({
    configured: true,
    isLoaded,
    isSignedIn: Boolean(user),
    userId: user?.id ?? null,
    email: user?.email ?? null,
    getToken,
    signUp,
    signIn,
    signOut,
  }), [getToken, isLoaded, signIn, signOut, signUp, user]);

  return <CustomerAuthContext.Provider value={value}>{children}</CustomerAuthContext.Provider>;
}

export function useCustomerAuth() {
  const value = useContext(CustomerAuthContext);
  if (!value) throw new Error("useCustomerAuth must be used inside CustomerAuthProvider");
  return value;
}
