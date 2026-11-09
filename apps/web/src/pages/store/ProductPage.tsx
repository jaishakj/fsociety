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
import { productSizesForCategory, type ProductSize } from "@/lib/productSizing";
import { useCartStore } from "@/stores/cartStore";
import { useWishlistStore } from "@/stores/wishlistStore";
import { ProductSizePicker } from "@/components/product/ProductSizePicker";

const LOW_STOCK_THRESHOLD = 5;

export default function ProductPage() {
  const { slug } = useParams();
  const { data: product, isLoading, isError } = useProduct(slug);
  const { data: related } = useRelatedProducts(product?.category.slug, product?.id);
  const [added, setAdded] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [selectedSize, setSelectedSize] = useState<ProductSize | null>(null);
  const addItem = useCartStore((state) => state.addItem);
  const isWishlisted = useWishlistStore((state) => (product ? state.has(product.id) : false));
  const toggleWishlist = useWishlistStore((state) => state.toggle);

  useEffect(() => {
    setSelectedIndex(0);
    setQuantity(1);
    setSelectedSize(null);
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
  const availableSizes = productSizesForCategory(product.category.slug, product.category.name);

  const handleAddToBag = () => {
    setAdded(addItem(product, quantity, selectedSize));
  };

  return (
    <div className="relative pb-36 md:pb-24">
      <AmbientGlow />

      <nav
        aria-label="Breadcrumb"
        className="relative z-10 mt-4 flex min-w-0 flex-wrap items-center gap-2 text-xs text-[var(--color-steel)] sm:text-sm md:mt-6"
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

      <section aria-label={`${product.name} product details`} className="relative z-10 mt-3 md:hidden">
        <div className="relative mx-auto aspect-[4/5] max-h-[68svh] overflow-hidden rounded-[28px] border border-white/10 bg-[var(--color-panel)]">
          {activeImage ? (
            <img
              src={activeImage.url}
              alt={activeImage.alt ?? product.name}
              className="h-full w-full object-contain object-center"
            />
          ) : (
            <div className="flex h-full items-center justify-center px-6 text-center text-sm text-[var(--color-steel)]">
              Product image unavailable
            </div>
          )}
          {product.images.length > 1 ? (
            <span className="absolute bottom-3 left-3 rounded-full border border-white/10 bg-[var(--color-void)]/80 px-3 py-1.5 font-mono text-xs text-[var(--color-paper)] backdrop-blur">
              {selectedIndex + 1} / {product.images.length}
            </span>
          ) : null}
          <button
            type="button"
            data-cursor
            onClick={() => toggleWishlist(product)}
            aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
            className="absolute right-3 top-3 flex min-h-12 min-w-12 items-center justify-center rounded-full border border-white/15 bg-[var(--color-void)]/80 backdrop-blur transition-colors hover:bg-[var(--color-panel)]"
          >
            <Heart
              size={18}
              className={isWishlisted ? "fill-[var(--color-signal)] text-[var(--color-signal)]" : "text-[var(--color-paper)]"}
            />
          </button>
        </div>

        {product.images.length > 1 ? (
          <div aria-label="Product photos" className="mobile-filter-scroll -mx-4 mt-3 flex gap-2 overflow-x-auto px-4 pb-1">
            {product.images.map((image, index) => (
              <button
                key={image.id}
                type="button"
                data-cursor
                aria-label={`Show image ${index + 1} of ${product.images.length}`}
                aria-pressed={index === selectedIndex}
                onClick={() => setSelectedIndex(index)}
                className={`h-20 w-16 flex-none overflow-hidden rounded-xl border-2 bg-[var(--color-panel)] transition-colors ${
                  index === selectedIndex ? "border-[var(--color-signal)]" : "border-white/10"
                }`}
              >
                <img src={image.url} alt="" className="h-full w-full object-cover object-center" />
              </button>
            ))}
          </div>
        ) : null}

        <div className="mt-5">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-[var(--color-signal)]">
              {product.category.name}
            </span>
            {lowStock ? <Chip>Only {product.stock} left</Chip> : null}
          </div>
          <h1 className="mt-2 font-display text-3xl leading-tight text-[var(--color-paper)] sm:text-4xl">
            {product.name}
          </h1>
          <p className="mt-2 font-mono text-lg text-[var(--color-paper)]">
            {product.currency} {product.price}
          </p>
          {product.description ? (
            <p className="mt-4 whitespace-pre-line text-sm leading-relaxed text-[var(--color-steel)]">
              {product.description}
            </p>
          ) : null}

          {availableSizes.length > 0 ? (
            <div className="mt-6 border-t border-white/10 pt-5">
              <ProductSizePicker sizes={availableSizes} value={selectedSize} onChange={setSelectedSize} />
            </div>
          ) : null}

          {!outOfStock ? (
            <div className="mt-5 flex items-center justify-between border-t border-white/10 pt-4">
              <span className="text-sm text-[var(--color-steel)]">Quantity</span>
              <div className="flex items-center gap-1 rounded-full border border-white/10 bg-[var(--color-panel)] p-1">
                <button
                  type="button"
                  data-cursor
                  aria-label="Decrease quantity"
                  disabled={quantity <= 1}
                  onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                  className="flex min-h-11 min-w-11 items-center justify-center rounded-full text-[var(--color-steel)] transition-colors hover:bg-white/5 disabled:pointer-events-none disabled:opacity-30"
                >
                  <Minus size={14} />
                </button>
                <span className="font-mono w-8 text-center text-sm text-[var(--color-paper)]">{quantity}</span>
                <button
                  type="button"
                  data-cursor
                  aria-label="Increase quantity"
                  disabled={quantity >= product.stock}
                  onClick={() => setQuantity((q) => Math.min(product.stock, q + 1))}
                  className="flex min-h-11 min-w-11 items-center justify-center rounded-full text-[var(--color-steel)] transition-colors hover:bg-white/5 disabled:pointer-events-none disabled:opacity-30"
                >
                  <Plus size={14} />
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </section>

      <div className="hidden md:block">
        <DepthStackHero
          title={product.name}
          subtitle={product.description ?? ""}
          imageUrl={activeImage?.url ?? ""}
          specs={[{ label: "Price", value: `${product.currency} ${product.price}` }]}
        />
      </div>

      {availableSizes.length > 0 ? (
        <div className="relative z-10 mt-8 hidden rounded-2xl border border-white/10 bg-[var(--color-panel)] p-5 sm:p-6 md:block">
          <ProductSizePicker sizes={availableSizes} value={selectedSize} onChange={setSelectedSize} />
        </div>
      ) : null}

      <div className="relative z-10 mt-10 hidden flex-wrap items-center gap-4 md:flex">
        {!outOfStock ? (
          <div className="flex items-center gap-3 rounded-full border border-white/10 bg-[var(--color-panel)] px-3 py-2">
            <button
              type="button"
              data-cursor
              aria-label="Decrease quantity"
              disabled={quantity <= 1}
              onClick={() => setQuantity((q) => Math.max(1, q - 1))}
              className="flex min-h-12 min-w-12 items-center justify-center rounded-full text-[var(--color-steel)] transition-colors hover:bg-white/5 disabled:pointer-events-none disabled:opacity-30"
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
              className="flex min-h-12 min-w-12 items-center justify-center rounded-full text-[var(--color-steel)] transition-colors hover:bg-white/5 disabled:pointer-events-none disabled:opacity-30"
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
          className="flex min-h-12 min-w-12 items-center justify-center rounded-full border border-white/10 bg-[var(--color-panel)] transition-colors hover:bg-white/5"
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
        <div className="relative z-10 mt-10 hidden gap-4 overflow-x-auto md:flex">
          {product.images.map((image, index) => (
            <button
              key={image.id}
              type="button"
              data-cursor
              aria-label={`Show image ${index + 1} of ${product.images.length}`}
              aria-pressed={index === selectedIndex}
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

      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-white/10 bg-[var(--color-void)]/95 px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] shadow-[0_-12px_32px_rgb(0_0_0/0.25)] backdrop-blur-xl md:hidden">
        <Button variant="primary" disabled={outOfStock} onClick={handleAddToBag} className="w-full">
          {outOfStock ? "Out of stock" : added ? "Added to bag" : "Add to bag"}
        </Button>
      </div>

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
