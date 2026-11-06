import gsap from "gsap";
import { useEffect, useRef, useState } from "react";

import { useProducts } from "@/hooks/useProducts";

const INTRO_SEEN_KEY = "fsociety-showreel-seen";
const INTRO_DURATION = 15;

const FALLBACK_LOOKS = [
  {
    src: "/hero-model.png",
    alt: "FSOCIETY campaign portrait",
    title: "The new collection",
    isMark: false,
  },
  {
    src: "/reality-hero.jpg",
    alt: "FSOCIETY occasionwear campaign portrait",
    title: "Occasionwear, in motion",
    isMark: false,
  },
  {
    src: "/favicon.svg",
    alt: "FSOCIETY sliced F logo",
    title: "FSOCIETY",
    isMark: true,
  },
];

const SCENE_COPY = [
  {
    eyebrow: "A COLLECTION FILM",
    title: "HIT HARD.",
    line: "Dresses built for the person who refuses to blend in.",
  },
  {
    eyebrow: "LOOK TWO",
    title: "OWN THE ROOM.",
    line: "Find the piece that feels like you.",
  },
  {
    eyebrow: "THE NEW COLLECTION",
    title: "YOUR ENTRANCE.",
    line: "Wear your own point of view.",
  },
];

function shouldShowShowreel() {
  if (typeof window === "undefined" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return false;
  }

  try {
    return window.sessionStorage.getItem(INTRO_SEEN_KEY) !== "1";
  } catch {
    return false;
  }
}

export function IntroShowreel() {
  const [visible, setVisible] = useState(shouldShowShowreel);
  const rootRef = useRef<HTMLDivElement>(null);
  const skipRef = useRef<HTMLButtonElement>(null);
  const { data } = useProducts({ page: 1, page_size: 4, sort: "newest" }, visible);

  const productLooks = data?.items
    .filter((product) => product.images.length > 0)
    .slice(0, 3)
    .map((product) => ({
      src: product.images[0].url,
      alt: product.images[0].alt || product.name,
      title: product.name,
      isMark: false,
    }));
  const looks = FALLBACK_LOOKS.map((fallback, index) => productLooks?.[index] ?? fallback);

  useEffect(() => {
    if (!visible || !rootRef.current) return;

    try {
      window.sessionStorage.setItem(INTRO_SEEN_KEY, "1");
    } catch {
      // The intro still plays when storage is unavailable; it simply won't persist the dismissal.
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    skipRef.current?.focus({ preventScroll: true });

    const root = rootRef.current;
    const select = gsap.utils.selector(root);
    const scenes = select<HTMLElement>(".showreel-scene");
    const images = select<HTMLImageElement>(".showreel-image");
    const timeline = gsap.timeline({
      onComplete: () => setVisible(false),
    });

    timeline.fromTo(
      select(".showreel-logo-lockup"),
      { autoAlpha: 0, y: 18, scale: 0.96 },
      { autoAlpha: 1, y: 0, scale: 1, duration: 0.8, ease: "power3.out" },
      0,
    );
    timeline.fromTo(
      select(".showreel-rule"),
      { scaleX: 0, transformOrigin: "left center" },
      { scaleX: 1, duration: 0.8, ease: "power2.inOut" },
      0.55,
    );
    timeline.fromTo(
      select(".showreel-progress-fill"),
      { scaleX: 0, transformOrigin: "left center" },
      { scaleX: 1, duration: INTRO_DURATION, ease: "none" },
      0,
    );

    scenes.forEach((scene, index) => {
      const start = [1.2, 5.1, 9.1][index];
      const exit = start + 3.2;
      const image = images[index];

      timeline.fromTo(
        scene,
        { autoAlpha: 0, xPercent: index === 0 ? 3 : 0 },
        { autoAlpha: 1, xPercent: 0, duration: 0.75, ease: "power3.out" },
        start,
      );
      if (image) {
        timeline.fromTo(
          image,
          { scale: 1.12, xPercent: index % 2 === 0 ? 2 : -2 },
          { scale: 1, xPercent: 0, duration: 4, ease: "power1.out" },
          start,
        );
      }
      timeline.to(scene, { autoAlpha: 0, xPercent: index % 2 === 0 ? -2 : 2, duration: 0.58 }, exit);
    });

    timeline.fromTo(
      select(".showreel-outro"),
      { autoAlpha: 0, scale: 0.97 },
      { autoAlpha: 1, scale: 1, duration: 0.85, ease: "power3.out" },
      12.5,
    );
    timeline.to(root, { autoAlpha: 0, duration: 0.38, ease: "power2.in" }, 14.62);

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setVisible(false);
      } else if (event.key === "Tab") {
        event.preventDefault();
        skipRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKeyDown);

    return () => {
      window.removeEventListener("keydown", onKeyDown);
      timeline.kill();
      gsap.set(root, { clearProps: "all" });
      document.body.style.overflow = previousOverflow;
    };
  }, [visible]);

  if (!visible) return null;

  const skip = () => setVisible(false);

  return (
    <div
      ref={rootRef}
      className="showreel-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="FSOCIETY collection film"
    >
      <div className="showreel-grid" aria-hidden="true" />

      <header className="showreel-header">
        <div className="showreel-logo-lockup">
          <img className="showreel-logo-mark" src="/favicon.svg" alt="" />
          <span className="showreel-wordmark">FSOCIETY</span>
        </div>
        <span className="showreel-edition">COLLECTION FILM&nbsp; / &nbsp;00:15</span>
        <button ref={skipRef} type="button" className="showreel-skip" onClick={skip} data-cursor>
          Skip intro <span aria-hidden="true">↗</span>
        </button>
      </header>

      <div className="showreel-rule" aria-hidden="true" />

      <main className="showreel-stage">
        {looks.map((look, index) => (
          <section className={`showreel-scene showreel-scene--${index + 1}`} key={index}>
            <div className="showreel-copy">
              <p className="showreel-eyebrow">
                <span className="showreel-live-dot" aria-hidden="true" />
                {SCENE_COPY[index].eyebrow}
              </p>
              <h1 className="showreel-title">{SCENE_COPY[index].title}</h1>
              <p className="showreel-description">{SCENE_COPY[index].line}</p>
              <p className="showreel-look-name">{look.title}</p>
            </div>

            <div className={`showreel-frame${look.isMark ? " showreel-frame--mark" : ""}`}>
              <span className="showreel-frame-index">0{index + 1}</span>
              <img className="showreel-image" src={look.src} alt={look.alt} />
              <span className="showreel-frame-edge" aria-hidden="true" />
            </div>
          </section>
        ))}

        <section className="showreel-outro" aria-label="FSOCIETY">
          <img src="/favicon.svg" alt="" className="showreel-outro-mark" />
          <p className="showreel-outro-word">FSOCIETY</p>
          <p className="showreel-outro-line">Wear your own point of view.</p>
        </section>
      </main>

      <footer className="showreel-footer" aria-hidden="true">
        <span>01 — 03&nbsp; / &nbsp;NEW COLLECTION</span>
        <div className="showreel-progress"><span className="showreel-progress-fill" /></div>
        <span>FS / 2026</span>
      </footer>
    </div>
  );
}
