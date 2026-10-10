import type { ReactNode } from "react";

export function StateMessage({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="py-24 text-center">
      <p className="text-[var(--color-paper)]">{title}</p>
      {description ? <p className="mt-2 text-sm text-[var(--color-steel)]">{description}</p> : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
