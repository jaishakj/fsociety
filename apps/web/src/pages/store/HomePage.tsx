import { Link } from "react-router-dom";

import { DepthStackHero } from "@/components/hero/DepthStackHero";
import { ProductCard } from "@/components/product/ProductCard";
import { AmbientGlow } from "@/components/ui/AmbientGlow";
import { Button } from "@/components/ui/Button";
import { StateMessage } from "@/components/ui/StateMessage";
import { useProducts } from "@/hooks/useProducts";

export default function HomePage() {
  const { data, isLoading, isError, refetch } = useProducts({ page: 1, sort: "newest" });

  return (
    <div className="relative pb-24">
      <AmbientGlow />

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

      <section className="relative z-10 mt-10 flex flex-col items-start justify-between gap-4 rounded-3xl border border-white/10 bg-[var(--color-panel)] p-8 md:flex-row md:items-center">
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

      <section className="relative z-10 mt-16">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="font-display text-2xl text-[var(--color-paper)]">New arrivals</h2>
          <Link to="/shop" data-cursor className="font-mono text-xs uppercase text-[var(--color-steel)]">
            View all
          </Link>
        </div>

        {isError ? (
          <StateMessage
            title="Couldn't load new arrivals"
            action={
              <Button variant="outline" data-cursor onClick={() => refetch()}>
                Retry
              </Button>
            }
          />
        ) : isLoading ? (
          <p className="text-[var(--color-steel)]">Loading&hellip;</p>
        ) : (data?.items.length ?? 0) === 0 ? (
          <p className="text-[var(--color-steel)]">No products yet.</p>
        ) : (
          <div className="-mx-4 flex snap-x snap-mandatory gap-4 overflow-x-auto px-4 pb-4">
            {data!.items.map((product) => (
              <div key={product.id} className="w-[70%] flex-shrink-0 snap-start sm:w-[45%] lg:w-[30%]">
                <ProductCard product={product} />
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
