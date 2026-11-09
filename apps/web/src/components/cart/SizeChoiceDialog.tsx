import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { X } from "lucide-react";

import { productSizesForCategory } from "@/lib/productSizing";
import { useCartStore } from "@/stores/cartStore";
import { handleDialogKeyDown, useDialogFocusRestore } from "@/components/ui/dialogKeyboard";

export function SizeChoiceDialog() {
  const pending = useCartStore((state) => state.pendingSizeSelection);
  const chooseSize = useCartStore((state) => state.choosePendingSize);
  const close = useCartStore((state) => state.closeSizePrompt);
  const reduceMotion = useReducedMotion();
  const dialogRef = useDialogFocusRestore<HTMLElement>(Boolean(pending));
  const sizes = pending
    ? productSizesForCategory(
        pending.kind === "add" ? pending.product.category.slug : pending.categorySlug,
        pending.kind === "add" ? pending.product.category.name : pending.categoryName,
      )
    : [];

  return (
    <AnimatePresence>
      {pending ? (
        <>
          <motion.div
            className="fixed inset-0 z-[1100] bg-black/70 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={reduceMotion ? { duration: 0.12 } : undefined}
            onClick={close}
            aria-hidden="true"
          />
          <motion.div
            className="fixed inset-0 z-[1101] flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={reduceMotion ? { duration: 0.12 } : undefined}
          >
            <motion.section
              ref={dialogRef}
              role="dialog"
              aria-modal="true"
              aria-labelledby="size-dialog-title"
              onKeyDown={(event) => handleDialogKeyDown(event, close)}
              className="w-full max-w-md rounded-3xl border border-white/10 bg-[var(--color-panel)] p-6 shadow-2xl sm:p-8"
              initial={reduceMotion ? { opacity: 0 } : { opacity: 0, y: 12, scale: 0.98 }}
              animate={reduceMotion ? { opacity: 1 } : { opacity: 1, y: 0, scale: 1 }}
              exit={reduceMotion ? { opacity: 0 } : { opacity: 0, y: 8, scale: 0.98 }}
              transition={reduceMotion ? { duration: 0.12 } : { type: "spring", bounce: 0, duration: 0.28 }}
            >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 id="size-dialog-title" className="font-display text-2xl text-[var(--color-paper)]">
                  Choose your size
                </h2>
                <p className="mt-2 text-sm leading-6 text-[var(--color-steel)]">
                  Select a size for {pending.kind === "add" ? pending.product.name : pending.productName} to add it to your bag.
                </p>
              </div>
              <button
                type="button"
                data-cursor
                onClick={close}
                aria-label="Close size selection"
                className="flex min-h-12 min-w-12 shrink-0 items-center justify-center rounded-full text-[var(--color-steel)] transition-colors hover:bg-white/5 hover:text-[var(--color-paper)]"
              >
                <X size={18} />
              </button>
            </div>

            <div
              role="group"
              aria-label="Choose a clothing size"
              className={`mt-7 grid gap-2 ${sizes.length > 5 ? "grid-cols-6" : "grid-cols-5"}`}
            >
              {sizes.map((size) => (
                <button
                  key={size}
                  type="button"
                  data-cursor
                  onClick={() => chooseSize(size)}
                  className="flex min-h-12 items-center justify-center rounded-full border border-white/10 text-sm text-[var(--color-paper)] transition-colors hover:border-[var(--color-signal)] hover:bg-[var(--color-signal)]/10 hover:text-[var(--color-signal)]"
                >
                  {size}
                </button>
              ))}
            </div>

            <p className="mt-4 text-xs text-[var(--color-steel)]">Your selection is saved with this bag item.</p>
            </motion.section>
          </motion.div>
        </>
      ) : null}
    </AnimatePresence>
  );
}
