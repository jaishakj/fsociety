import { motion } from "motion/react";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type NativeButtonProps = Omit<
  ButtonHTMLAttributes<HTMLButtonElement>,
  "onDrag" | "onDragStart" | "onDragEnd" | "onAnimationStart" | "onAnimationEnd" | "onAnimationIteration"
>;

interface ButtonProps extends NativeButtonProps {
  children: ReactNode;
  variant?: "primary" | "outline";
}

export function Button({ children, variant = "primary", className = "", ...rest }: ButtonProps) {
  const base =
    "inline-flex items-center justify-center rounded-full px-6 py-3 text-sm font-medium transition-colors";
  const styles =
    variant === "primary"
      ? "bg-[var(--color-signal)] text-[var(--color-void)]"
      : "border border-[var(--color-steel)] text-[var(--color-paper)]";

  return (
    <motion.button
      data-cursor
      whileTap={{ scale: 0.96 }}
      whileHover={{ scale: 1.03 }}
      transition={{ type: "spring", bounce: 0, duration: 0.3 }}
      className={`${base} ${styles} ${className}`}
      {...rest}
    >
      {children}
    </motion.button>
  );
}
