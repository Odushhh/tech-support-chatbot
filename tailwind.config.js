/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}', // for pages
    './components/**/*.{js,ts,jsx,tsx}', // for components
    './app/**/*.{js,ts,jsx,tsx}', // if using the app directory
    './src/**/*.{js,ts,jsx,tsx}', // Add this line if your files are in the src directory
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

