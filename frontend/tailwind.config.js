/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        border: "var(--border)",
        primary: {
          DEFAULT: "#00c6ff",
          dark: "#0072ff"
        },
        secondary: {
          DEFAULT: "#f35588",
          dark: "#a83f60"
        },
        card: {
          DEFAULT: "#ffffff",
          dark: "#1e1e2f"
        }
      },
    },
  },
  plugins: [],
}
