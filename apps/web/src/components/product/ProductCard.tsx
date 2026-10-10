import gsap from "gsap";
import { Heart } from "lucide-react";
import type { MouseEvent } from "react";
import { useRef } from "react";
import { Link } from "react-router-dom";

import { useWishlistStore } from "@/stores/wishlistStore";
import type { Product } from "@/types/product";

export function ProductCard({ product }: { product: Product }) {
  const cardRef = useRef<HTMLAnchorElement>(null);
  const isWishlisted = useWishlistStore((state) => state.has(product.id));
  const toggleWishlist = useWishlistStore((state) => state.toggle);

  function onMove(e: MouseEvent<HTMLAnchorElement>) {
    const el = cardRef.current;
    if (!el || window.matchMedia("(hover: none), (pointer: coarse)").matches) return;
    const rect = el.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width - 0.5;
    const py = (e.clientY - rect.top) / rect.height - 0.5;
    gsap.to(el, { rotateY: px * 8, rotateX: -py * 8, duration: 0.4, ease: "power3.out" });
  }

  function onLeave() {
    const el = cardRef.current;
    if (!el) return;
    gsap.to(el, { rotateY: 0, rotateX: 0, duration: 0.5, ease: "power3.out" });
  }

  function onWishlistClick(e: MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    e.stopPropagation();
    toggleWishlist(product);
  }

  const image = product.images[0]?.url;

  return (
    <Link
      ref={cardRef}
      to={`/product/${product.slug}`}
      data-cursor
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      className="group block rounded-3xl border border-white/10 bg-[var(--color-panel)] p-4"
      style={{ perspective: "800px" }}
    >
      <div className="relative aspect-[3/4] overflow-hidden rounded-2xl bg-black/40">
        {image ? (
          <img
            src={image}
            alt={product.name}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : null}
        <button
          type="button"
          data-cursor
          onClick={onWishlistClick}
          aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
          className="absolute right-2 top-2 rounded-full bg-black/50 p-2 backdrop-blur transition-colors hover:bg-black/70"
        >
          <Heart
            size={16}
            className={isWishlisted ? "fill-[var(--color-signal)] text-[var(--color-signal)]" : "text-white"}
          />
        </button>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <h3 className="text-sm text-[var(--color-paper)]">{product.name}</h3>
        <span className="font-mono rounded-full bg-black/30 px-2 py-1 text-xs text-[var(--color-signal)]">
          {product.currency} {product.price}
        </span>
      </div>
    </Link>
  );
}
