/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class", // enables 'dark:' variants based on a .dark class
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
