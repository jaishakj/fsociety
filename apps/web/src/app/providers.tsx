import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode, useState } from "react";
import { CartSyncProvider } from "@/auth/CartSync";
import { CustomerAuthProvider } from "@/auth/customerAuth";

export function Providers({ children }: { children: ReactNode }) {
  const [client] = useState(() => new QueryClient());
  return (
    <QueryClientProvider client={client}>
      <CustomerAuthProvider>
        <CartSyncProvider>{children}</CartSyncProvider>
      </CustomerAuthProvider>
    </QueryClientProvider>
  );
}
