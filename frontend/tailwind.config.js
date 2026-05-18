/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
      colors: {
        primary: "#1ed760",
        "primary-dark": "#1db954",
        "primary-light": "#1fdf64",
        "bg-base": "#121212",
        "bg-surface": "#181818",
        "bg-elevated": "#1f1f1f",
        "bg-highlight": "#252525",
        "bg-card": "#272727",
        "text-base": "#ffffff",
        "text-subdued": "#b3b3b3",
        "text-muted": "#6a6a6a",
        "border-default": "#4d4d4d",
        "border-subtle": "#282828",
        "border-bright": "#7c7c7c",
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
