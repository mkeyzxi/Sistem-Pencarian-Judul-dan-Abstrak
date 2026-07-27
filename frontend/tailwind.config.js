/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: "#1ed760",
        "primary-dark": "#1db954",
        "primary-light": "#1fdf64",
        "bg-base": "var(--app-bg-base)",
        "bg-surface": "var(--app-bg-surface)",
        "bg-elevated": "var(--app-bg-elevated)",
        "bg-highlight": "var(--app-bg-highlight)",
        "bg-card": "var(--app-bg-card)",
        "text-base": "var(--app-text-base)",
        "text-subdued": "var(--app-text-subdued)",
        "text-muted": "var(--app-text-muted)",
        "text-accent": "var(--app-text-accent)",
        "border-default": "var(--app-border-default)",
        "border-subtle": "var(--app-border-subtle)",
        "border-bright": "var(--app-border-bright)",
        negative: "#f3727f",
        warning: "#ffa42b",
        info: "#539df5",
      },
      fontFamily: {
        display: ["Inter", "Helvetica Neue", "helvetica", "arial", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "4px",
        sm: "2px",
        md: "6px",
        lg: "8px",
        xl: "10px",
        "2xl": "16px",
        pill: "500px",
        full: "9999px",
      },
      boxShadow: {
        "spotify-medium": "rgba(0,0,0,0.3) 0px 8px 8px",
        "spotify-heavy": "rgba(0,0,0,0.5) 0px 8px 24px",
      },
    },
  },
}
