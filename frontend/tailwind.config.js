/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'google-green': '#0F9D58',
        'google-blue': '#4285F4',
        'google-yellow': '#F4B400',
        'google-red': '#DB4437',
        'play-dark': '#202124',
        'play-card': '#1F1F1F',
        'play-surface': '#28292C',
      },
      fontFamily: {
        sans: ['"Google Sans"', 'Roboto', 'Arial', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
