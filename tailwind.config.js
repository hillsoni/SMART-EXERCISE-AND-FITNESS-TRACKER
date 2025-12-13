// /** @type {import('tailwindcss').Config} */
// module.exports = {
//   content: [
//     "./index.html",              // <-- root index.html for Vite
//     "./src/**/*.{js,jsx,ts,tsx}" // all React components
//   ],
//   theme: {
//     extend: {
//       colors: {
//         dark: "#0a0a0a",
//         blue: "#1d4ed8",
//         green: "#16a34a",
//         yellow: "#facc15",
//         orange: "#f97316",
//       },
//     },
//   },
//   plugins: [],
// };

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",              // root file for Vite
    "./src/**/*.{js,jsx,ts,tsx}" // all React files
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
