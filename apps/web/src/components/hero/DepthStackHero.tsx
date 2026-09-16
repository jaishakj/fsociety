import gsap from "gsap";
import { useEffect, useRef } from "react";

interface DepthStackHeroProps {
  eyebrow?: string;
  title: string;
  subtitle: string;
  imageUrl: string;
  specs?: { label: string; value: string }[];
}

export function DepthStackHero({
  eyebrow,
  title,
  subtitle,
  imageUrl,
  specs = [],
}: DepthStackHeroProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const image = imageRef.current;
    const text = textRef.current;
    if (!container || !image || !text) return;

    gsap.fromTo(text, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.9, ease: "power3.out" });
    gsap.fromTo(
      image,
      { opacity: 0, y: 40, scale: 0.98 },
      { opacity: 1, y: 0, scale: 1, duration: 1, ease: "power3.out", delay: 0.1 },
    );

    if (window.matchMedia("(hover: none), (pointer: coarse)").matches) return;

    function onMove(e: MouseEvent) {
      const rect = container!.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width - 0.5;
      const py = (e.clientY - rect.top) / rect.height - 0.5;
      gsap.to(image, { rotateY: px * 6, rotateX: -py * 6, duration: 0.6, ease: "power3.out" });
      gsap.to(text, { x: px * -12, duration: 0.8, ease: "power3.out" });
    }

    function onLeave() {
      gsap.to(image, { rotateY: 0, rotateX: 0, duration: 0.6, ease: "power3.out" });
      gsap.to(text, { x: 0, duration: 0.8, ease: "power3.out" });
    }

    container.addEventListener("mousemove", onMove);
    container.addEventListener("mouseleave", onLeave);
    return () => {
      container.removeEventListener("mousemove", onMove);
      container.removeEventListener("mouseleave", onLeave);
    };
  }, []);

  return (
    <section
      ref={containerRef}
      className="relative mt-6 overflow-hidden rounded-[32px] border border-white/10 bg-[var(--color-panel)] px-6 py-16 md:px-16 md:py-24"
      style={{ perspective: "1000px" }}
    >
      <div
        ref={textRef}
        className="font-display pointer-events-none absolute inset-x-0 top-1/2 -translate-y-1/2 select-none text-center text-[18vw] leading-none text-white/5 md:text-[9vw]"
      >
        {title}
      </div>

      <div className="relative z-10 flex flex-col items-center gap-8 md:flex-row md:items-end md:justify-between">
        <div className="max-w-md">
          {eyebrow ? (
            <span className="font-mono mb-4 inline-block text-xs uppercase tracking-[0.2em] text-[var(--color-signal)]">
              {eyebrow}
            </span>
          ) : null}
          <h1 className="font-display text-5xl text-[var(--color-paper)] md:text-6xl">{title}</h1>
          <p className="mt-4 text-[var(--color-steel)]">{subtitle}</p>
        </div>

        <div ref={imageRef} className="relative w-full max-w-sm" style={{ transformStyle: "preserve-3d" }}>
          <div
            className="absolute inset-x-8 bottom-0 h-16 rounded-full blur-2xl"
            style={{ background: "var(--color-signal-dim)", opacity: 0.6 }}
          />
          {imageUrl ? (
            <img src={imageUrl} alt={title} className="relative w-full rounded-2xl object-cover" />
          ) : null}
        </div>
      </div>

      {specs.length > 0 ? (
        <div className="relative z-10 mt-10 flex flex-wrap gap-3">
          {specs.map((spec) => (
            <span
              key={spec.label}
              className="font-mono rounded-full border border-white/10 bg-black/30 px-3 py-1 text-[11px] uppercase tracking-wide text-[var(--color-steel)]"
            >
              {spec.label}: <span className="text-[var(--color-paper)]">{spec.value}</span>
            </span>
          ))}
        </div>
      ) : null}
    </section>
  );
}
