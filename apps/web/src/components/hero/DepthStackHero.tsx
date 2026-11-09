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

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const intro = gsap.timeline();
    intro.fromTo(text, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.9, ease: "power3.out" });
    gsap.fromTo(
      image,
      { opacity: 0, y: 40, scale: 0.98 },
      { opacity: 1, y: 0, scale: 1, duration: 1, ease: "power3.out", delay: 0.1 },
    );

    const touchDevice = window.matchMedia("(hover: none), (pointer: coarse)").matches;
    if (touchDevice) {
      const float = gsap.to(image, {
        y: -6,
        duration: 3.2,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
        delay: 1.1,
      });
      return () => {
        intro.kill();
        float.kill();
        gsap.killTweensOf(image);
      };
    }

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
      intro.kill();
      gsap.killTweensOf([image, text]);
    };
  }, []);

  return (
    <section
      ref={containerRef}
      className="relative mt-3 rounded-[28px] border border-white/10 bg-[var(--color-panel)] px-5 py-7 sm:mt-6 sm:px-8 sm:py-10 md:rounded-[32px] md:px-16 md:py-24"
      style={{ perspective: "1000px" }}
    >
      <div
        ref={textRef}
        className="font-display pointer-events-none absolute inset-x-0 top-1/2 hidden -translate-y-1/2 select-none text-center text-[9vw] leading-none text-white/5 lg:block"
      >
        {title}
      </div>

      <div className="relative z-10 flex flex-col items-center gap-5 sm:gap-7 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-md">
          <h1 className="font-display text-4xl text-[var(--color-paper)] sm:text-5xl md:text-6xl">{title}</h1>
          {eyebrow ? <p className="mt-2 text-xs text-[var(--color-steel)] sm:text-sm">{eyebrow}</p> : null}
          <p className="mt-3 max-w-prose text-sm leading-relaxed text-[var(--color-steel)] sm:text-base md:mt-4">{subtitle}</p>
        </div>
      </div>

      {imageUrl ? (
        <div
          ref={imageRef}
          className="relative z-10 mx-auto mt-5 w-full max-w-[18rem] sm:mt-7 sm:max-w-sm lg:absolute lg:right-10 lg:-top-4 lg:bottom-0 lg:mx-0 lg:mt-0 lg:w-auto xl:right-16"
          style={{ transformStyle: "preserve-3d" }}
        >
          <div className="relative aspect-[3/4] w-full overflow-hidden rounded-2xl md:h-full md:w-auto">
            <img src={imageUrl} alt={title} className="h-full w-full object-contain object-center md:object-cover md:object-top" />
          </div>
        </div>
      ) : null}

      {specs.length > 0 ? (
        <div className="relative z-10 mt-5 flex flex-wrap gap-2 sm:mt-8 sm:gap-3">
          {specs.map((spec) => (
            <span
              key={spec.label}
              className="rounded-full border border-white/10 bg-black/30 px-3 py-1 text-xs text-[var(--color-steel)]"
            >
              {spec.label}: <span className="text-[var(--color-paper)]">{spec.value}</span>
            </span>
          ))}
        </div>
      ) : null}
    </section>
  );
}
