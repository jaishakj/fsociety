import { FallingLeaves } from "falling-leaves/react";

export function FallingLeavesField() {
  return (
    <FallingLeaves
      fullScreen
      count={12}
      size={[9, 19]}
      speed={[0.35, 0.85]}
      wind={[-0.2, 0.25]}
      sway={[0.35, 0.8]}
      rotationSpeed={[-0.9, 0.9]}
      colors={["#ff2e43", "#7a1420", "#b75843", "#ffc15c"]}
      shapes={["maple", "oak", "ginkgo"]}
      opacity={0.38}
      zIndex={0}
      respectReducedMotion
    />
  );
}
