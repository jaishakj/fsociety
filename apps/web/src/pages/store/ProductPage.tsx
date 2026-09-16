import { useState } from "react";
import { useParams } from "react-router-dom";

import { DepthStackHero } from "@/components/hero/DepthStackHero";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { useProduct } from "@/hooks/useProducts";

export default function ProductPage() {
  const { slug } = useParams();
  const { data: product, isLoading } = useProduct(slug);
  const [added, setAdded] = useState(false);

  if (isLoading || !product) {
    return <p className="py-24 text-center text-[var(--color-steel)]">Loading…</p>;
  }

  return (
    <div className="pb-24">
      <DepthStackHero
        eyebrow={product.category.name}
        title={product.name}
        subtitle={product.description ?? ""}
        imageUrl={product.images[0]?.url ?? ""}
        specs={[
          { label: "Price", value: `${product.currency} ${product.price}` },
          { label: "SKU", value: product.slug.toUpperCase() },
          { label: "Stock", value: `${product.stock} left` },
        ]}
      />

      <div className="mt-10 flex flex-wrap items-center gap-4">
        <Button variant="primary" data-cursor onClick={() => setAdded(true)}>
          {added ? "Added to bag" : "Add to bag"}
        </Button>
        <Chip>{product.category.name}</Chip>
      </div>

      {product.images.length > 1 ? (
        <div className="mt-10 flex gap-4 overflow-x-auto">
          {product.images.map((image) => (
            <img
              key={image.id}
              src={image.url}
              alt={image.alt ?? product.name}
              className="h-40 w-32 flex-shrink-0 rounded-xl object-cover"
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}
