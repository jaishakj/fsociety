import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { diwaliCampaign } from "@/config/diwaliCampaign";
import { getCountdown } from "@/config/diwaliCountdown";

const SECOND = 1_000;

export function DiwaliSaleSection() {
  const [now, setNow] = useState(() => Date.now());
  const endAt = diwaliCampaign.endAt;

  useEffect(() => {
    if (!endAt) return;
    const initial = getCountdown(endAt);
    if (!initial || initial.expired) return;

    const timer = window.setInterval(() => {
      const current = Date.now();
      setNow(current);
      if (getCountdown(endAt, current)?.expired) window.clearInterval(timer);
    }, SECOND);
    return () => window.clearInterval(timer);
  }, [endAt]);

  const countdown = endAt ? getCountdown(endAt, now) : null;
  const activeCountdown = countdown && !countdown.expired ? countdown : null;

  return (
    <section className="relative z-10 mt-16 overflow-hidden rounded-3xl border border-[var(--color-signal)]/25 bg-[var(--color-panel)] px-6 py-9 sm:px-10 sm:py-12">
      <div className="pointer-events-none absolute -right-20 -top-24 h-64 w-64 rounded-full border border-[var(--color-signal)]/15" aria-hidden="true" />
      <div className="pointer-events-none absolute -right-10 -top-14 h-44 w-44 rounded-full border border-[var(--color-signal)]/10" aria-hidden="true" />
      <div className="relative grid gap-8 md:grid-cols-[1fr_auto] md:items-end">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">A seasonal edit</p>
          <h2 className="mt-3 font-display text-4xl leading-none text-[var(--color-paper)] sm:text-6xl">{diwaliCampaign.heading}</h2>
          <p className="mt-4 max-w-xl text-sm leading-6 text-[var(--color-steel)]">{diwaliCampaign.description}</p>
        </div>
        <div className="flex flex-col items-start gap-4 md:items-end">
          {activeCountdown ? (
            <div className="flex gap-2 sm:gap-3" aria-label="Time remaining in the Diwali campaign">
              {([
                [activeCountdown.days, "Days"],
                [activeCountdown.hours, "Hours"],
                [activeCountdown.minutes, "Minutes"],
                [activeCountdown.seconds, "Seconds"],
              ] as const).map(([value, label]) => (
                <div key={label} className="min-w-14 text-center sm:min-w-16">
                  <span className="block font-mono text-2xl tabular-nums text-[var(--color-paper)] sm:text-3xl">
                    {String(value).padStart(label === "Days" ? 1 : 2, "0")}
                  </span>
                  <span className="mt-1 block text-[10px] uppercase tracking-wider text-[var(--color-steel)]">{label}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[var(--color-steel)]" role="status">
              {countdown?.expired ? "This campaign has ended." : "Campaign dates will be announced soon."}
            </p>
          )}
          {activeCountdown ? (
            <Link to={diwaliCampaign.shopUrl} className="inline-flex rounded-full bg-[var(--color-signal)] px-6 py-3 text-sm font-medium text-[var(--color-void)] transition-transform hover:-translate-y-0.5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--color-signal)]">
              SHOP THE SALE
            </Link>
          ) : null}
        </div>
      </div>
    </section>
  );
}
