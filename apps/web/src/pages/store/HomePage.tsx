import { Link } from "react-router-dom";

import { DepthStackHero } from "@/components/hero/DepthStackHero";
import { ProductGrid } from "@/components/product/ProductGrid";
import { Button } from "@/components/ui/Button";
import { useProducts } from "@/hooks/useProducts";

export default function HomePage() {
  const { data } = useProducts({ page: 1, sort: "newest" });

  return (
    <div className="pb-24">
      <DepthStackHero
        eyebrow="New Collection"
        title="HIT HARD"
        subtitle="Dresses built for the person who refuses to blend in."
        imageUrl="/hero-model.png"
        specs={[
          { label: "Drop", value: "SS26" },
          { label: "Pieces", value: "48" },
        ]}
      />

      <section className="mt-10 flex flex-col items-start justify-between gap-4 rounded-3xl border border-white/10 bg-[var(--color-panel)] p-8 md:flex-row md:items-center">
        <div>
          <span className="font-mono text-xs uppercase tracking-wide text-[var(--color-signal)]">
            Limited
          </span>
          <h2 className="font-display mt-2 text-3xl text-[var(--color-paper)]">
            40% off select styles
          </h2>
        </div>
        <Link to="/shop">
          <Button variant="primary">Shop the drop</Button>
        </Link>
      </section>

      <section className="mt-16">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="font-display text-2xl text-[var(--color-paper)]">New arrivals</h2>
          <Link to="/shop" data-cursor className="font-mono text-xs uppercase text-[var(--color-steel)]">
            View all
          </Link>
        </div>
        <ProductGrid products={data?.items ?? []} />
      </section>
    </div>
  );
}
