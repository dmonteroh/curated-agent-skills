/** @type {import('tailwindcss').Config} */
module.exports = {
  // Common choice: toggle dark mode by adding/removing a "dark" class on <html> or <body>.
  darkMode: "class",

  // Only needed when classes are produced dynamically (string concatenation, CMS-driven).
  // Keep patterns tightly scoped to a namespace you own to avoid CSS bloat.
  safelist: [
    {
      pattern: /^(bg|text|border|ring|outline|divide|shadow)-ui-.*$/,
      variants: ["hover", "focus", "focus-within"],
    },
  ],

  // Include every path that can generate class names.
  content: [
    "./src/**/*.{html,js,ts,jsx,tsx,svelte,vue,md,mdx}",
    // Example: include a UI library if it ships templates that contain Tailwind classes.
    // "./node_modules/<your-lib>/**/*.{html,js,ts,svelte,vue,jsx,tsx}",
  ],

  theme: {
    extend: {
      colors: {
        // Semantic UI tokens backed by CSS variables.
        ui: {
          canvas: "var(--ui-canvas)",
          "surface-1": "var(--ui-surface-1)",
          "surface-2": "var(--ui-surface-2)",
          "surface-3": "var(--ui-surface-3)",
          text: "var(--ui-text)",
          "text-muted": "var(--ui-text-muted)",
          border: "var(--ui-border)",
          "border-muted": "var(--ui-border-muted)",
          action: "var(--ui-action)",
          "action-secondary": "var(--ui-action-secondary)",
          "action-tertiary": "var(--ui-action-tertiary)",
          selection: "var(--ui-selection)",
          success: "var(--ui-success)",
          warning: "var(--ui-warning)",
          error: "var(--ui-error)",
        },
      },

      textColor: {
        ui: {
          "on-action": "var(--ui-on-action)",
          "on-action-secondary": "var(--ui-on-action-secondary)",
          "on-action-tertiary": "var(--ui-on-action-tertiary)",
          "on-selection": "var(--ui-on-selection)",
          "on-success": "var(--ui-on-success)",
          "on-warning": "var(--ui-on-warning)",
          "on-error": "var(--ui-on-error)",
        },
      },

      fontFamily: {
        base: ["var(--theme-font-family-base)", "system-ui", "sans-serif"],
        heading: ["var(--theme-font-family-heading)", "system-ui", "sans-serif"],
      },

      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "0.875rem" }],
        "3xs": ["0.5625rem", { lineHeight: "0.75rem" }],
        "4xs": ["0.5rem", { lineHeight: "0.7rem" }],
      },
    },
  },

  plugins: [],
};

