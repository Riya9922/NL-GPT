/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "highlight-verified": "#f0fdf4",     // Extremely light pastel green
        "highlight-pending": "#fefef0",      // Extremely light pastel yellow
        "highlight-unsupported": "#fee2e2",  // Pastel red
        "highlight-na": "#f1f5f9",           // Pastel slate
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
  ],
};
