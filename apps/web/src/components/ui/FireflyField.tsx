import { Pause, Play } from "lucide-react";
import { useState, type CSSProperties } from "react";

const FIREFLIES = Array.from({ length: 18 }, (_, index) => ({
  x: 4 + ((index * 47) % 92),
  y: 5 + ((index * 61) % 88),
  driftX: ((index * 17) % 65) - 32,
  driftY: ((index * 29) % 55) - 27,
  duration: 13 + (index % 6) * 2,
  delay: -((index % 8) * 1.4),
  size: 2 + (index % 2),
  glow: 8 + ((index * 7) % 10),
}));

export function FireflyField() {
  const [paused, setPaused] = useState(false);

  return (
    <>
      <div className={`firefly-field${paused ? " firefly-field--paused" : ""}`} aria-hidden="true">
        {FIREFLIES.map((firefly, index) => (
          <span
            key={index}
            className="firefly"
            style={
              {
                "--firefly-x": `${firefly.x}%`,
                "--firefly-y": `${firefly.y}%`,
                "--firefly-drift-x": `${firefly.driftX}px`,
                "--firefly-drift-y": `${firefly.driftY}px`,
                "--firefly-duration": `${firefly.duration}s`,
                "--firefly-delay": `${firefly.delay}s`,
                "--firefly-size": `${firefly.size}px`,
                "--firefly-glow": `${firefly.glow}px`,
              } as CSSProperties
            }
          />
        ))}
      </div>
      <button
        type="button"
        className="firefly-toggle"
        onClick={() => setPaused((isPaused) => !isPaused)}
        aria-label={paused ? "Resume firefly animation" : "Pause firefly animation"}
        title={paused ? "Resume firefly animation" : "Pause firefly animation"}
      >
        {paused ? <Play size={14} aria-hidden="true" /> : <Pause size={14} aria-hidden="true" />}
      </button>
    </>
  );
}
