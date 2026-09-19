import { AnimatePresence, motion } from "motion/react";
import { X } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { useCartStore } from "@/stores/cartStore";

export function CartDrawer() {
  const items = useCartStore((state) => state.items);
  const isOpen = useCartStore((state) => state.isOpen);
  const close = useCartStore((state) => state.close);
  const removeItem = useCartStore((state) => state.removeItem);
  const updateQuantity = useCartStore((state) => state.updateQuantity);
  const totalPrice = useCartStore((state) => state.totalPrice());

  return (
    <AnimatePresence>
      {isOpen ? (
        <>
          <motion.div
            className="fixed inset-0 z-[997] bg-black/60"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={close}
          />
          <motion.aside
            className="fixed inset-y-0 right-0 z-[998] flex w-full max-w-sm flex-col overflow-y-auto bg-[var(--color-panel)] p-6"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", bounce: 0, duration: 0.35 }}
          >
            <div className="flex items-center justify-between">
              <h2 className="font-display text-xl text-[var(--color-paper)]">Your bag</h2>
              <button
                data-cursor
                onClick={close}
                aria-label="Close"
                className="rounded-full p-2 hover:bg-white/5"
              >
                <X size={18} />
              </button>
            </div>

            <div className="mt-6 flex-1">
              {items.length === 0 ? (
                <p className="text-sm text-[var(--color-steel)]">Your bag is empty.</p>
              ) : (
                <ul className="space-y-4">
                  {items.map((item) => (
                    <li key={item.id} className="flex gap-4">
                      {item.image ? (
                        <img src={item.image} alt={item.name} className="h-20 w-16 rounded-lg object-cover" />
                      ) : (
                        <div className="h-20 w-16 rounded-lg bg-black/40" />
                      )}
                      <div className="flex-1">
                        <p className="text-sm text-[var(--color-paper)]">{item.name}</p>
                        <p className="font-mono mt-1 text-xs text-[var(--color-signal)]">
                          {item.currency} {item.price}
                        </p>
                        <div className="mt-2 flex items-center gap-2">
                          <button
                            data-cursor
                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                            className="rounded-full border border-white/10 px-2 text-xs text-[var(--color-steel)]"
                            aria-label="Decrease quantity"
                          >
                            &minus;
                          </button>
                          <span className="font-mono text-xs text-[var(--color-paper)]">{item.quantity}</span>
                          <button
                            data-cursor
                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                            className="rounded-full border border-white/10 px-2 text-xs text-[var(--color-steel)]"
                            aria-label="Increase quantity"
                          >
                            +
                          </button>
                        </div>
                      </div>
                      <button
                        data-cursor
                        onClick={() => removeItem(item.id)}
                        aria-label="Remove item"
                        className="text-[var(--color-steel)] hover:text-[var(--color-signal)]"
                      >
                        <X size={14} />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {items.length > 0 ? (
              <div className="mt-6 border-t border-white/10 pt-4">
                <div className="flex items-center justify-between text-sm text-[var(--color-paper)]">
                  <span>Subtotal</span>
                  <span className="font-mono">INR {totalPrice.toFixed(2)}</span>
                </div>
                {/* No checkout backend yet, this is intentionally a placeholder */}
                <Button variant="outline" className="mt-4 w-full" disabled>
                  Checkout (coming soon)
                </Button>
              </div>
            ) : null}
          </motion.aside>
        </>
      ) : null}
    </AnimatePresence>
  );
}
