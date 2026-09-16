import { Outlet } from "react-router-dom";

import { CustomCursor } from "@/components/cursor/CustomCursor";
import { Footer } from "@/components/layout/Footer";
import { NavBar } from "@/components/layout/NavBar";

export function Shell() {
  return (
    <div className="min-h-screen bg-[var(--color-void)] px-4 pb-4 pt-4">
      <CustomCursor />
      <NavBar />
      <main className="mx-auto max-w-6xl">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
