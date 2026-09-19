import { useState } from "react";
import { useParams } from "react-router-dom";

import { DepthStackHero } from "@/components/hero/DepthStackHero";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { useProduct } from "@/hooks/useProducts";
import { useCartStore } from "@/stores/cartStore";

export default function ProductPage() {
  const { slug } = useParams();
  const { data: product, isLoading } = useProduct(slug);
  const [added, setAdded] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const addItem = useCartStore((state) => state.addItem);

  if (isLoading || !product) {
    return <p className="py-24 text-center text-[var(--color-steel)]">Loading…</p>;
  }

  const activeImage = product.images[selectedIndex] ?? product.images[0];

  function handleAddToBag() {
    addItem(product!);
    setAdded(true);
  }

  return (
    <div className="pb-24">
      <DepthStackHero
        eyebrow={product.category.name}
        title={product.name}
        subtitle={product.description ?? ""}
        imageUrl={activeImage?.url ?? ""}
        specs={[{ label: "Price", value: `${product.currency} ${product.price}` }]}
      />

      <div className="mt-10 flex flex-wrap items-center gap-4">
        <Button variant="primary" data-cursor onClick={handleAddToBag}>
          {added ? "Added to bag" : "Add to bag"}
        </Button>
        <Chip>{product.category.name}</Chip>
      </div>

      {product.images.length > 1 ? (
        <div className="mt-10 flex gap-4 overflow-x-auto">
          {product.images.map((image, index) => (
            <button
              key={image.id}
              type="button"
              data-cursor
              onClick={() => setSelectedIndex(index)}
              className={`flex-shrink-0 overflow-hidden rounded-xl border-2 transition-colors ${
                index === selectedIndex ? "border-[var(--color-signal)]" : "border-transparent"
              }`}
            >
              <img
                src={image.url}
                alt={image.alt ?? product.name}
                className="h-40 w-32 object-cover"
              />
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
