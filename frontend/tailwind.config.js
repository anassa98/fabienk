/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        upa: {
          primary: "#16a34a",
          dark: "#0f172a",
          accent: "#f59e0b",
        },
      },
    },
  },
  plugins: [],
};
