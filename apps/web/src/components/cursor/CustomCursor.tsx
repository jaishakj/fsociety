import gsap from "gsap";
import { useEffect, useRef } from "react";

export function CustomCursor() {
  const dotRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (window.matchMedia("(hover: none), (pointer: coarse)").matches) return;

    const dot = dotRef.current;
    const ring = ringRef.current;
    if (!dot || !ring) return;

    const moveDotX = gsap.quickTo(dot, "x", { duration: 0.1, ease: "power3" });
    const moveDotY = gsap.quickTo(dot, "y", { duration: 0.1, ease: "power3" });
    const moveRingX = gsap.quickTo(ring, "x", { duration: 0.35, ease: "power3" });
    const moveRingY = gsap.quickTo(ring, "y", { duration: 0.35, ease: "power3" });

    function onMove(e: MouseEvent) {
      moveDotX(e.clientX);
      moveDotY(e.clientY);
      moveRingX(e.clientX);
      moveRingY(e.clientY);
    }

    function onOver(e: MouseEvent) {
      if ((e.target as HTMLElement).closest("[data-cursor]")) {
        ring?.classList.add("cursor-ring--active");
      }
    }

    function onOut(e: MouseEvent) {
      if ((e.target as HTMLElement).closest("[data-cursor]")) {
        ring?.classList.remove("cursor-ring--active");
      }
    }

    window.addEventListener("mousemove", onMove);
    document.addEventListener("mouseover", onOver);
    document.addEventListener("mouseout", onOut);

    return () => {
      window.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseover", onOver);
      document.removeEventListener("mouseout", onOut);
    };
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 z-[999] hidden md:block">
      <div ref={ringRef} className="cursor-ring" />
      <div ref={dotRef} className="cursor-dot" />
    </div>
  );
}
