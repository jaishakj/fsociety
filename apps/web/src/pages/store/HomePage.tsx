import { ArrowUpRight } from "lucide-react";
import { Link } from "react-router-dom";

import { DiwaliSaleSection } from "@/components/home/DiwaliSaleSection";
import { DepthStackHero } from "@/components/hero/DepthStackHero";
import { ProductCard } from "@/components/product/ProductCard";
import { AmbientGlow } from "@/components/ui/AmbientGlow";
import { Button } from "@/components/ui/Button";
import { StateMessage } from "@/components/ui/StateMessage";
import { useCategories, useProducts } from "@/hooks/useProducts";
import { usePageMeta } from "@/hooks/usePageMeta";
import type { Product } from "@/types/product";

export default function HomePage() {
  usePageMeta("FSOCIETY | Dresses built to stand out", "Discover the latest FSOCIETY styles and shop the current collection.", "/");
  const { data, isLoading, isError, refetch } = useProducts({ page: 1, page_size: 4, sort: "newest" });
  const { data: categories, isLoading: categoriesLoading, isError: categoriesError } = useCategories();
  const sareeCategory = categories?.find((category) => /saree/i.test(`${category.name} ${category.slug}`));
  const sarees = useProducts(
    { page: 1, page_size: 4, sort: "newest", category: sareeCategory?.slug },
    Boolean(sareeCategory),
  );

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

      <DiwaliSaleSection />

      <section className="relative z-10 mt-20">
        <div className="mb-7 flex items-end justify-between gap-4">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--color-signal)]">Find your edit</p>
            <h2 className="mt-2 font-display text-3xl text-[var(--color-paper)]">Shop by category</h2>
          </div>
          <Link to="/shop" className="shrink-0 text-sm text-[var(--color-steel)] transition-colors hover:text-[var(--color-paper)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-signal)]">All styles <span aria-hidden="true">↗</span></Link>
        </div>
        {categories?.length ? (
          <div className="grid grid-cols-1 gap-px overflow-hidden rounded-2xl border border-white/10 bg-white/10 sm:grid-cols-2 lg:grid-cols-3">
            {categories.map((category, index) => (
              <Link
                key={category.id}
                to={`/shop?category=${encodeURIComponent(category.slug)}`}
                className="group flex min-h-24 items-center justify-between bg-[var(--color-panel)] px-5 py-6 transition-colors hover:bg-white/[0.06] focus-visible:outline focus-visible:outline-2 focus-visible:outline-inset focus-visible:outline-[var(--color-signal)] sm:px-7"
              >
                <span className="flex items-center gap-4">
                  <span className="font-mono text-xs text-[var(--color-signal)]">{String(index + 1).padStart(2, "0")}</span>
                  <span className="font-display text-xl text-[var(--color-paper)]">{category.name}</span>
                </span>
                <ArrowUpRight size={18} className="text-[var(--color-steel)] transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" aria-hidden="true" />
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-sm text-[var(--color-steel)]">{categoriesLoading ? "Loading categories…" : categoriesError ? "Categories are temporarily unavailable." : "Categories will appear here as the collection grows."}</p>
        )}
      </section>

      {sareeCategory && (sarees.data?.items.length ?? 0) > 0 ? (
        <ProductSection eyebrow="The saree edit" title="Timeless drapes. Contemporary attitude." products={sarees.data!.items} href={`/shop?category=${encodeURIComponent(sareeCategory.slug)}`} linkLabel="View the edit" />
      ) : null}

      <section className="relative z-10 mt-20 grid overflow-hidden rounded-3xl bg-[var(--color-signal)] text-[var(--color-void)] md:grid-cols-[1fr_auto] md:items-end">
        <div className="p-7 sm:p-10">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em]">Wear your own point of view</p>
          <h2 className="mt-4 max-w-2xl font-display text-3xl leading-tight sm:text-5xl">A little less expected. A lot more you.</h2>
        </div>
        <Link to="/shop" className="mx-7 mb-7 inline-flex items-center gap-2 self-end text-sm font-semibold underline decoration-current/40 underline-offset-4 transition-opacity hover:opacity-70 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--color-void)] sm:mx-10 sm:mb-10">
          Explore the collection <ArrowUpRight size={16} aria-hidden="true" />
        </Link>
      </section>

      <section className="relative z-10 mt-20">
        <div className="mb-7 flex items-end justify-between gap-4">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--color-signal)]">Fresh from the collection</p>
            <h2 className="mt-2 font-display text-3xl text-[var(--color-paper)]">New arrivals</h2>
          </div>
          <Link to="/shop" data-cursor className="shrink-0 text-sm text-[var(--color-steel)] transition-colors hover:text-[var(--color-paper)]">View all</Link>
        </div>

        {isError ? (
          <StateMessage title="Couldn't load new arrivals" action={<Button variant="outline" data-cursor onClick={() => refetch()}>Retry</Button>} />
        ) : isLoading ? (
          <p className="text-[var(--color-steel)]">Loading…</p>
        ) : (data?.items.length ?? 0) === 0 ? (
          <p className="text-[var(--color-steel)]">New pieces will appear here as they arrive.</p>
        ) : (
          <div className="grid grid-cols-2 gap-x-3 gap-y-6 sm:grid-cols-2 sm:gap-5 lg:grid-cols-4">
            {data!.items.map((product) => <ProductCard key={product.id} product={product} />)}
          </div>
        )}
      </section>

      <section className="relative z-10 mt-20 flex flex-col items-start justify-between gap-6 border-t border-white/10 pt-8 sm:flex-row sm:items-end">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.18em] text-[var(--color-steel)]">FSOCIETY / New collection</p>
          <h2 className="mt-3 font-display text-3xl text-[var(--color-paper)] sm:text-4xl">Your next favourite starts here.</h2>
        </div>
        <Link to="/shop"><Button>Explore all styles</Button></Link>
      </section>
    </div>
  );
}

function ProductSection({ eyebrow, title, products, href, linkLabel }: {
  eyebrow: string;
  title: string;
  products: Product[];
  href: string;
  linkLabel: string;
}) {
  return (
    <section className="relative z-10 mt-20">
      <div className="mb-7 flex items-end justify-between gap-4">
        <div><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--color-signal)]">{eyebrow}</p><h2 className="mt-2 font-display text-3xl text-[var(--color-paper)]">{title}</h2></div>
        <Link to={href} className="shrink-0 text-sm text-[var(--color-steel)] transition-colors hover:text-[var(--color-paper)]">{linkLabel}</Link>
      </div>
      <div className="grid grid-cols-2 gap-x-3 gap-y-6 sm:gap-5 lg:grid-cols-4">{products.map((product) => <ProductCard key={product.id} product={product} />)}</div>
    </section>
  );
}
