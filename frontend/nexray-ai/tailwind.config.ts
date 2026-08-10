import type { Config } from "tailwindcss";

// NexRay AI — Design Token System
// Every color, radius, shadow, and spacing value used across the app
// should be pulled from here — never hardcoded in components.

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        // Core clinical palette
        primary: {
          DEFAULT: "#0F4C81", // Medical Blue
          hover: "#0C3D68",
          foreground: "#FFFFFF",
        },
        secondary: {
          DEFAULT: "#2E7D6E", // Clinical Teal
          hover: "#256459",
          foreground: "#FFFFFF",
        },
        accent: {
          DEFAULT: "#4CAF50", // Healthy Green
          foreground: "#FFFFFF",
        },
        warning: {
          DEFAULT: "#F59E0B",
          bg: "#FFFBEB",
          foreground: "#78350F",
        },
        critical: {
          DEFAULT: "#DC2626",
          bg: "#FEF2F2",
          foreground: "#7F1D1D",
        },
        info: {
          DEFAULT: "#2563EB",
          bg: "#EFF6FF",
          foreground: "#1E3A8A",
        },
        success: {
          DEFAULT: "#4CAF50",
          bg: "#ECFDF5",
          foreground: "#065F46",
        },

        // Surfaces
        background: "#F7FAFC",
        surface: "#FFFFFF",
        "surface-secondary": "#F9FBFD",

        // Text
        "text-primary": "#1F2937",
        "text-secondary": "#6B7280",
        "text-disabled": "#CBD5E1",

        // Borders
        border: "#E5E7EB",
        "border-strong": "#D1D5DB",

        // shadcn/ui compatibility tokens (mapped onto clinical palette)
        input: "#E5E7EB",
        ring: "#0F4C81",
        foreground: "#1F2937",
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#1F2937",
        },
        popover: {
          DEFAULT: "#FFFFFF",
          foreground: "#1F2937",
        },
        muted: {
          DEFAULT: "#F9FBFD",
          foreground: "#6B7280",
        },
        destructive: {
          DEFAULT: "#DC2626",
          foreground: "#FFFFFF",
        },
      },
      fontSize: {
        display: ["32px", { lineHeight: "40px", fontWeight: "700" }],
        "page-title": ["32px", { lineHeight: "40px", fontWeight: "700" }],
        "section-title": ["24px", { lineHeight: "32px", fontWeight: "600" }],
        "card-title": ["18px", { lineHeight: "26px", fontWeight: "600" }],
        subtitle: ["16px", { lineHeight: "24px", fontWeight: "500" }],
        body: ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "body-sm": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        caption: ["14px", { lineHeight: "20px", fontWeight: "400" }],
        label: ["14px", { lineHeight: "20px", fontWeight: "500" }],
        tiny: ["12px", { lineHeight: "16px", fontWeight: "400" }],
      },
      spacing: {
        // 8pt grid — use these instead of arbitrary values
        1: "4px",
        2: "8px",
        3: "12px",
        4: "16px",
        5: "20px",
        6: "24px",
        8: "32px",
        10: "40px",
        12: "48px",
        16: "64px",
      },
      borderRadius: {
        sm: "8px",
        DEFAULT: "12px",
        md: "12px",
        lg: "16px",
        xl: "20px",
        full: "9999px",
      },
      boxShadow: {
        sm: "0 1px 2px 0 rgba(15, 23, 42, 0.04)",
        DEFAULT: "0 1px 3px 0 rgba(15, 23, 42, 0.06), 0 1px 2px -1px rgba(15, 23, 42, 0.06)",
        md: "0 4px 12px -2px rgba(15, 23, 42, 0.08)",
        lg: "0 12px 24px -4px rgba(15, 23, 42, 0.10)",
        none: "none",
      },
      transitionDuration: {
        fast: "120ms",
        DEFAULT: "180ms",
        slow: "280ms",
      },
      zIndex: {
        dropdown: "1000",
        sticky: "1100",
        overlay: "1200",
        modal: "1300",
        toast: "1400",
        tooltip: "1500",
      },
      keyframes: {
        "fade-in": { from: { opacity: "0" }, to: { opacity: "1" } },
        "slide-up": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-1000px 0" },
          "100%": { backgroundPosition: "1000px 0" },
        },
      },
      animation: {
        "fade-in": "fade-in 180ms ease-out",
        "slide-up": "slide-up 220ms ease-out",
        shimmer: "shimmer 2s infinite linear",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
