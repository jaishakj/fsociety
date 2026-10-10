import { Heart } from "lucide-react";
import { Link } from "react-router-dom";

import { AmbientGlow } from "@/components/ui/AmbientGlow";
import { Button } from "@/components/ui/Button";
import { StateMessage } from "@/components/ui/StateMessage";
import { useCartStore } from "@/stores/cartStore";
import { useWishlistStore } from "@/stores/wishlistStore";

export default function WishlistPage() {
  const items = useWishlistStore((state) => state.items);
  const remove = useWishlistStore((state) => state.remove);
  const addToCart = useCartStore((state) => state.addItem);

  if (items.length === 0) {
    return (
      <StateMessage
        title="Your wishlist is empty"
        description="Tap the heart on any product to save it here."
        action={
          <Link to="/shop" data-cursor className="text-[var(--color-signal)] underline">
            Browse the shop
          </Link>
        }
      />
    );
  }

  return (
    <div className="relative py-10 pb-24">
      <AmbientGlow />

      <h1 className="relative z-10 font-display text-4xl text-[var(--color-paper)]">Wishlist</h1>

      <div className="relative z-10 mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((item) => (
          <div key={item.id} className="rounded-3xl border border-white/10 bg-[var(--color-panel)] p-4">
            <Link to={`/product/${item.slug}`} data-cursor className="block">
              <div className="aspect-[3/4] overflow-hidden rounded-2xl bg-black/40">
                {item.image ? (
                  <img src={item.image} alt={item.name} className="h-full w-full object-cover" />
                ) : null}
              </div>
              <div className="mt-4 flex items-center justify-between">
                <h3 className="text-sm text-[var(--color-paper)]">{item.name}</h3>
                <span className="font-mono rounded-full bg-black/30 px-2 py-1 text-xs text-[var(--color-signal)]">
                  {item.currency} {item.price}
                </span>
              </div>
            </Link>
            <div className="mt-4 flex gap-2">
              <Button
                variant="primary"
                data-cursor
                className="flex-1 !py-2 text-xs"
                onClick={() =>
                  addToCart({
                    id: item.id,
                    name: item.name,
                    price: item.price,
                    currency: item.currency,
                    images: item.image ? [{ id: item.id, url: item.image, alt: null, position: 0 }] : [],
                  })
                }
              >
                Add to bag
              </Button>
              <button
                type="button"
                data-cursor
                onClick={() => remove(item.id)}
                aria-label="Remove from wishlist"
                className="rounded-full border border-white/10 p-2 text-[var(--color-steel)] hover:text-[var(--color-signal)]"
              >
                <Heart size={16} className="fill-current" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
