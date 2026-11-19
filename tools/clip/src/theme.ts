// One theme for the whole clip. No colour, easing or spring is written anywhere else.
import { Easing } from "remotion";

export const theme = {
  colors: {
    bg: "#F5F2EC",
    surface: "#FFFFFF",
    ink: "#14161B",
    dim: "#6B7280",
    faint: "#A8ADB7",
    line: "#E3DED3",
    hero: "#2B5CFF", // the one accent: whatever the eye should be on
    heroSoft: "#E4EAFF",
    star: "#E9A23B",
    warn: "#E8622C", // the "before" colour: what goes wrong without the plugin
    good: "#1E8E5A", // a number that got better
    note: "#3D424D", // small print: dark enough to read on the light ground
    shadow: "rgba(20,22,27,0.10)",
  },
  fonts: { display: "Bricolage", body: "InterV", mono: "JBMono" },
  ease: {
    out: Easing.bezier(0.16, 1, 0.3, 1),
    inOut: Easing.bezier(0.83, 0, 0.17, 1),
    in: Easing.bezier(0.7, 0, 0.84, 0),
  },
  spring: {
    snappy: { damping: 14, stiffness: 160, mass: 0.6 },
    smooth: { damping: 20, stiffness: 90, mass: 1 },
    bouncy: { damping: 11, stiffness: 170, mass: 0.7 },
    slow: { damping: 30, stiffness: 60, mass: 1 },
  },
} as const;
