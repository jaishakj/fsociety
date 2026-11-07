'use client';

import React, { useState, useRef, useEffect } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import { Check, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { dropdownTransition } from '@/lib/motion-tokens';

export type DropdownSide = 'top' | 'right' | 'bottom' | 'left';

export interface OriginDropdownItem {
  id: string;
  label: string;
  description?: string;
  icon?: React.ReactNode;
  destructive?: boolean;
  disabled?: boolean;
  selected?: boolean;
  onSelect?: () => void;
}

export interface OriginDropdownProps {
  /** Trigger element (rendered as a button by default) */
  trigger?: React.ReactNode;
  /** Items rendered in the menu */
  items?: OriginDropdownItem[];
  /** Pre-built menu content (alternative to items) */
  children?: React.ReactNode;
  /** Side the menu should open from */
  side?: DropdownSide;
  /** Align the menu against the start or end of its trigger */
  align?: 'start' | 'end';
  /** Optional controlled open state */
  open?: boolean;
  /** Default open state (uncontrolled) */
  defaultOpen?: boolean;
  /** Open state change callback */
  onOpenChange?: (open: boolean) => void;
  className?: string;
  /** Placeholder trigger content if no trigger provided */
  placeholder?: string;
  /** Accessible name for the trigger button */
  triggerAriaLabel?: string;
}

const sideTransform: Record<DropdownSide, { x: number; y: number }> = {
  top: { x: 0, y: 8 },
  bottom: { x: 0, y: -8 },
  left: { x: 8, y: 0 },
  right: { x: -8, y: 0 },
};

const sideStyles: Record<DropdownSide, string> = {
  top: 'bottom-full mb-2',
  bottom: 'top-full mt-2',
  left: 'right-full mr-2',
  right: 'left-full ml-2',
};

const alignStyles: Record<DropdownSide, Record<'start' | 'end', string>> = {
  top: { start: 'left-0', end: 'right-0' },
  bottom: { start: 'left-0', end: 'right-0' },
  left: { start: 'top-0', end: 'bottom-0' },
  right: { start: 'top-0', end: 'bottom-0' },
};

const sideOrigin: Record<DropdownSide, Record<'start' | 'end', string>> = {
  top: { start: 'origin-bottom-left', end: 'origin-bottom-right' },
  bottom: { start: 'origin-top-left', end: 'origin-top-right' },
  left: { start: 'origin-top-right', end: 'origin-bottom-right' },
  right: { start: 'origin-top-left', end: 'origin-bottom-left' },
};

/**
 * OriginDropdown — Origin-aware expansion rather than simply appearing.
 * The menu materializes from the chosen side with a slight scale (0.96 -> 1)
 * and an outward -> inward translation, so the perceived origin is the edge
 * of the trigger closest to the menu.
 */
export const OriginDropdown: React.FC<OriginDropdownProps> = ({
  trigger,
  items,
  children,
  side = 'bottom',
  align = 'start',
  open: controlledOpen,
  defaultOpen = false,
  onOpenChange,
  className,
  placeholder = 'Open menu',
  triggerAriaLabel,
}) => {
  const [internalOpen, setInternalOpen] = useState(defaultOpen);
  const isControlled = controlledOpen !== undefined;
  const open = isControlled ? controlledOpen : internalOpen;
  const rootRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const menuId = React.useId();
  const shouldReduceMotion = useReducedMotion();

  const setOpen = (next: boolean) => {
    if (!isControlled) setInternalOpen(next);
    onOpenChange?.(next);
  };

  const closeAndFocusTrigger = () => {
    setOpen(false);
    window.requestAnimationFrame(() => triggerRef.current?.focus());
  };

  const focusOutsideRoot = (reverse: boolean) => {
    const root = rootRef.current;
    if (!root) return;

    const outsideItems = Array.from(
      document.querySelectorAll<HTMLElement>(
        'a[href], button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])'
      )
    ).filter((element) => !root.contains(element));
    const before = outsideItems.filter(
      (element) => element.compareDocumentPosition(root) & Node.DOCUMENT_POSITION_FOLLOWING
    );
    const after = outsideItems.filter(
      (element) => root.compareDocumentPosition(element) & Node.DOCUMENT_POSITION_FOLLOWING
    );
    const target = reverse ? before[before.length - 1] : after[0];

    window.requestAnimationFrame(() => target?.focus());
  };

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: PointerEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeAndFocusTrigger();
    };
    document.addEventListener('pointerdown', onPointerDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('pointerdown', onPointerDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  useEffect(() => {
    if (!open || children) return;
    window.requestAnimationFrame(() => {
      menuRef.current?.querySelector<HTMLButtonElement>('[role="menuitemradio"]:not(:disabled)')?.focus();
    });
  }, [open, children]);

  const offsetT = sideTransform[side];
  const handleMenuKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    const enabledItems = Array.from(
      menuRef.current?.querySelectorAll<HTMLButtonElement>('[role="menuitemradio"]:not(:disabled)') ?? []
    );
    const currentIndex = enabledItems.indexOf(document.activeElement as HTMLButtonElement);
    let nextIndex: number | undefined;

    if (event.key === 'ArrowDown') nextIndex = (currentIndex + 1) % enabledItems.length;
    if (event.key === 'ArrowUp') nextIndex = (currentIndex - 1 + enabledItems.length) % enabledItems.length;
    if (event.key === 'Home') nextIndex = 0;
    if (event.key === 'End') nextIndex = enabledItems.length - 1;
    if (event.key === 'Tab') {
      event.preventDefault();
      setOpen(false);
      focusOutsideRoot(event.shiftKey);
      return;
    }

    if (nextIndex !== undefined && enabledItems.length) {
      event.preventDefault();
      enabledItems[nextIndex]?.focus();
    }
  };

  return (
    <div ref={rootRef} className={cn('relative inline-block w-full sm:w-auto', className)}>
      <button
        ref={triggerRef}
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={menuId}
        aria-label={triggerAriaLabel}
        onClick={() => setOpen(!open)}
        onKeyDown={(event) => {
          if (event.key === 'ArrowDown' && !open) {
            event.preventDefault();
            setOpen(true);
          }
        }}
        data-cursor
        className="inline-flex min-h-12 w-full items-center justify-between gap-3 rounded-full border border-[var(--color-signal)] bg-[var(--color-panel)] px-5 text-sm font-medium text-[var(--color-paper)] transition-colors hover:bg-white/[0.03] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-signal)] sm:w-auto sm:min-w-40"
      >
        {trigger ?? <span>{placeholder}</span>}
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={shouldReduceMotion ? { duration: 0 } : dropdownTransition}
          className="text-[var(--color-steel)]"
        >
          <ChevronDown className="w-3.5 h-3.5" />
        </motion.span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            ref={menuRef}
            id={menuId}
            role="menu"
            initial={{
              opacity: 0,
              scale: shouldReduceMotion ? 1 : 0.96,
              x: shouldReduceMotion ? 0 : offsetT.x,
              y: shouldReduceMotion ? 0 : offsetT.y,
            }}
            animate={{ opacity: 1, scale: 1, x: 0, y: 0 }}
            exit={{
              opacity: 0,
              scale: shouldReduceMotion ? 1 : 0.97,
              x: shouldReduceMotion ? 0 : offsetT.x * 0.4,
              y: shouldReduceMotion ? 0 : offsetT.y * 0.4,
            }}
            transition={shouldReduceMotion ? { duration: 0 } : dropdownTransition}
            onKeyDown={handleMenuKeyDown}
            className={cn(
              'absolute z-50 w-[min(16rem,calc(100vw-2rem))] min-w-[11rem] overflow-hidden rounded-xl border border-white/10 bg-[var(--color-panel)] py-1.5 text-[var(--color-paper)] shadow-[0_18px_45px_rgba(0,0,0,0.42)]',
              sideStyles[side],
              alignStyles[side][align],
              sideOrigin[side][align]
            )}
          >
            {children ? (
              children
            ) : (
              <ul className="flex flex-col">
                {items?.map((item) => (
                  <li key={item.id}>
                    <button
                      type="button"
                      data-cursor
                      role="menuitemradio"
                      aria-checked={Boolean(item.selected)}
                      disabled={item.disabled}
                      onClick={() => {
                        if (item.disabled) return;
                        item.onSelect?.();
                        closeAndFocusTrigger();
                      }}
                      className={cn(
                        'flex min-h-11 w-full items-center justify-between gap-3 px-4 py-2.5 text-left text-sm transition-colors focus-visible:bg-white/5 focus-visible:outline-none',
                        item.disabled
                          ? 'cursor-not-allowed opacity-40'
                          : item.destructive
                            ? 'text-[var(--color-signal)] hover:bg-white/5'
                            : item.selected
                              ? 'text-[var(--color-signal)] hover:bg-white/5'
                              : 'text-[var(--color-paper)] hover:bg-white/5'
                      )}
                    >
                      <span className="flex min-w-0 items-center gap-2.5">
                        {item.icon && <span className="shrink-0 text-[var(--color-steel)]">{item.icon}</span>}
                        <span className="flex min-w-0 flex-col">
                          <span className="leading-tight font-medium">{item.label}</span>
                          {item.description && <span className="mt-0.5 text-xs text-[var(--color-steel)]">{item.description}</span>}
                        </span>
                      </span>
                      {item.selected && <Check aria-hidden="true" className="h-4 w-4 shrink-0" />}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
