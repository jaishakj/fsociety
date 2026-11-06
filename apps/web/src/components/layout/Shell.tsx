import { Outlet } from "react-router-dom";

import { CartDrawer } from "@/components/cart/CartDrawer";
import { CustomCursor } from "@/components/cursor/CustomCursor";
import { Footer } from "@/components/layout/Footer";
import { IntroShowreel } from "@/components/layout/IntroShowreel";
import { NavBar } from "@/components/layout/NavBar";
import { SearchModal } from "@/components/search/SearchModal";
import { FireflyField } from "@/components/ui/FireflyField";

export function Shell() {
  return (
    <div className="relative isolate min-h-screen bg-[var(--color-void)] px-4 pb-4 pt-4">
      <IntroShowreel />
      <FireflyField />
      <CustomCursor />
      <CartDrawer />
      <SearchModal />
      <NavBar />
      <main className="relative z-[1] mx-auto max-w-6xl">
        <Outlet />
      </main>
      <div className="relative z-[1]">
        <Footer />
      </div>
    </div>
  );
}
