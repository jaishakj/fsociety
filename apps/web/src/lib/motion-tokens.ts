import type { Transition } from "motion/react";

export const dropdownTransition: Transition = {
  type: "spring",
  stiffness: 380,
  damping: 30,
  mass: 0.5,
};
