import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { X } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { handleDialogKeyDown, useDialogFocusRestore } from "@/components/ui/dialogKeyboard";
import { productUsesApparelSizes } from "@/lib/productSizing";
import { useCartStore } from "@/stores/cartStore";

export function CartDrawer() {
  const items = useCartStore((state) => state.items);
  const isOpen = useCartStore((state) => state.isOpen);
  const close = useCartStore((state) => state.close);
  const reduceMotion = useReducedMotion();
  const removeItem = useCartStore((state) => state.removeItem);
  const updateQuantity = useCartStore((state) => state.updateQuantity);
  const requestCartItemSize = useCartStore((state) => state.requestCartItemSize);
  const totalPrice = useCartStore((state) => state.totalPrice());
  const hasMissingSizes = items.some((item) =>
    productUsesApparelSizes(item.categorySlug, item.categoryName) && !item.size,
  );

  const dialogRef = useDialogFocusRestore<HTMLElement>(isOpen);

  return (
    <AnimatePresence>
      {isOpen ? (
        <>
          <motion.div
            className="fixed inset-0 z-[997] bg-black/60"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={reduceMotion ? { duration: 0.12 } : undefined}
            onClick={close}
          />
          <motion.aside
            ref={dialogRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="bag-title"
            onKeyDown={(event) => handleDialogKeyDown(event, close)}
            className="fixed inset-y-0 right-0 z-[998] flex w-full max-w-sm flex-col overflow-y-auto border-l border-white/10 bg-[var(--color-panel)] p-6"
            initial={reduceMotion ? { opacity: 0 } : { x: "100%" }}
            animate={reduceMotion ? { opacity: 1 } : { x: 0 }}
            exit={reduceMotion ? { opacity: 0 } : { x: "100%" }}
            transition={reduceMotion ? { duration: 0.12 } : { type: "spring", bounce: 0, duration: 0.35 }}
          >
            <div className="flex items-center justify-between">
              <h2 id="bag-title" className="font-display text-xl text-[var(--color-paper)]">Your bag</h2>
              <button
                data-cursor
                onClick={close}
                aria-label="Close bag"
                className="flex min-h-12 min-w-12 items-center justify-center rounded-full hover:bg-white/5"
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
                        {productUsesApparelSizes(item.categorySlug, item.categoryName) ? (
                          item.size ? (
                            <p className="mt-1 text-xs text-[var(--color-steel)]">Size {item.size}</p>
                          ) : (
                            <button
                              type="button"
                              data-cursor
                              onClick={() => requestCartItemSize(item.id)}
                              className="mt-1 rounded text-left text-xs text-[var(--color-signal)] underline underline-offset-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--color-signal)]"
                            >
                              Choose size
                            </button>
                          )
                        ) : null}
                        <div className="mt-2 flex items-center gap-1">
                          <button
                            data-cursor
                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                            className="min-h-12 min-w-10 rounded-full border border-white/10 text-xs text-[var(--color-steel)] transition-colors hover:bg-white/5"
                            aria-label={`Decrease quantity of ${item.name}`}
                          >
                            &minus;
                          </button>
                          <span className="font-mono text-xs text-[var(--color-paper)]">{item.quantity}</span>
                          <button
                            data-cursor
                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                            className="min-h-12 min-w-10 rounded-full border border-white/10 text-xs text-[var(--color-steel)] transition-colors hover:bg-white/5"
                            aria-label={`Increase quantity of ${item.name}`}
                          >
                            +
                          </button>
                        </div>
                      </div>
                      <button
                        data-cursor
                        onClick={() => removeItem(item.id)}
                        aria-label={`Remove ${item.name} from bag`}
                        className="flex min-h-12 min-w-12 items-center justify-center rounded-full text-[var(--color-steel)] transition-colors hover:bg-white/5 hover:text-[var(--color-signal)]"
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
                  <span>INR {totalPrice.toFixed(2)}</span>
                </div>
                <Link
                  to="/checkout"
                  data-cursor
                  onClick={(event) => {
                    if (hasMissingSizes) {
                      event.preventDefault();
                      const firstMissing = items.find((item) =>
                        productUsesApparelSizes(item.categorySlug, item.categoryName) && !item.size,
                      );
                      if (firstMissing) requestCartItemSize(firstMissing.id);
                      return;
                    }
                    close();
                  }}
                  className="mt-4 block"
                >
                  <Button variant="primary" className="w-full">
                    Checkout
                  </Button>
                </Link>
              </div>
            ) : null}
          </motion.aside>
        </>
      ) : null}
    </AnimatePresence>
  );
}
