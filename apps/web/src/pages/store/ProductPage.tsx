import { Heart, Minus, Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { DepthStackHero } from "@/components/hero/DepthStackHero";
import { ProductGrid } from "@/components/product/ProductGrid";
import { AmbientGlow } from "@/components/ui/AmbientGlow";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { StateMessage } from "@/components/ui/StateMessage";
import { useProduct, useRelatedProducts } from "@/hooks/useProducts";
import { useCartStore } from "@/stores/cartStore";
import { useWishlistStore } from "@/stores/wishlistStore";

const LOW_STOCK_THRESHOLD = 5;

export default function ProductPage() {
  const { slug } = useParams();
  const { data: product, isLoading, isError } = useProduct(slug);
  const { data: related } = useRelatedProducts(product?.category.slug, product?.id);
  const [added, setAdded] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const addItem = useCartStore((state) => state.addItem);
  const isWishlisted = useWishlistStore((state) => (product ? state.has(product.id) : false));
  const toggleWishlist = useWishlistStore((state) => state.toggle);

  useEffect(() => {
    setSelectedIndex(0);
    setQuantity(1);
    setAdded(false);
  }, [slug]);

  useEffect(() => {
    if (!added) return;
    const timeout = setTimeout(() => setAdded(false), 2000);
    return () => clearTimeout(timeout);
  }, [added]);

  if (isLoading) {
    return <p className="py-24 text-center text-[var(--color-steel)]">Loading&hellip;</p>;
  }

  if (isError || !product) {
    return (
      <StateMessage
        title="Product not found"
        description="This product may have been removed or the link is incorrect."
        action={
          <Link to="/shop" data-cursor className="text-[var(--color-signal)] underline">
            Back to shop
          </Link>
        }
      />
    );
  }

  const activeImage = product.images[selectedIndex] ?? product.images[0];
  const outOfStock = product.stock <= 0;
  const lowStock = !outOfStock && product.stock <= LOW_STOCK_THRESHOLD;

  const handleAddToBag = () => {
    addItem(product, quantity);
    setAdded(true);
  };

  return (
    <div className="relative pb-24">
      <AmbientGlow />

      <nav
        aria-label="Breadcrumb"
        className="font-mono relative z-10 mt-6 flex flex-wrap items-center gap-2 text-xs uppercase tracking-wide text-[var(--color-steel)]"
      >
        <Link to="/" data-cursor className="hover:text-[var(--color-paper)]">
          Home
        </Link>
        <span>/</span>
        <Link to="/shop" data-cursor className="hover:text-[var(--color-paper)]">
          Shop
        </Link>
        <span>/</span>
        <span>{product.category.name}</span>
        <span>/</span>
        <span className="text-[var(--color-paper)]">{product.name}</span>
      </nav>

      <DepthStackHero
        eyebrow={product.category.name}
        title={product.name}
        subtitle={product.description ?? ""}
        imageUrl={activeImage?.url ?? ""}
        specs={[{ label: "Price", value: `${product.currency} ${product.price}` }]}
      />

      <div className="relative z-10 mt-10 flex flex-wrap items-center gap-4">
        {!outOfStock ? (
          <div className="flex items-center gap-3 rounded-full border border-white/10 bg-[var(--color-panel)] px-3 py-2">
            <button
              type="button"
              data-cursor
              aria-label="Decrease quantity"
              disabled={quantity <= 1}
              onClick={() => setQuantity((q) => Math.max(1, q - 1))}
              className="text-[var(--color-steel)] disabled:opacity-30"
            >
              <Minus size={14} />
            </button>
            <span className="font-mono w-6 text-center text-sm text-[var(--color-paper)]">{quantity}</span>
            <button
              type="button"
              data-cursor
              aria-label="Increase quantity"
              disabled={quantity >= product.stock}
              onClick={() => setQuantity((q) => Math.min(product.stock, q + 1))}
              className="text-[var(--color-steel)] disabled:opacity-30"
            >
              <Plus size={14} />
            </button>
          </div>
        ) : null}

        <Button variant="primary" data-cursor disabled={outOfStock} onClick={handleAddToBag}>
          {outOfStock ? "Out of stock" : added ? "Added to bag" : "Add to bag"}
        </Button>

        <button
          type="button"
          data-cursor
          onClick={() => toggleWishlist(product)}
          aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
          className="rounded-full border border-white/10 bg-[var(--color-panel)] p-3"
        >
          <Heart
            size={18}
            className={isWishlisted ? "fill-[var(--color-signal)] text-[var(--color-signal)]" : "text-[var(--color-paper)]"}
          />
        </button>

        <Chip>{product.category.name}</Chip>
        {lowStock ? <Chip>Only {product.stock} left</Chip> : null}
      </div>

      {product.images.length > 1 ? (
        <div className="relative z-10 mt-10 flex gap-4 overflow-x-auto">
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
              <img src={image.url} alt={image.alt ?? product.name} className="h-40 w-32 object-cover" />
            </button>
          ))}
        </div>
      ) : null}

      {related && related.length > 0 ? (
        <section className="relative z-10 mt-20">
          <h2 className="font-display text-2xl text-[var(--color-paper)]">You might also like</h2>
          <div className="mt-6">
            <ProductGrid products={related} />
          </div>
        </section>
      ) : null}
    </div>
  );
}
