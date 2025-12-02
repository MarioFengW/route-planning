/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'royal-blue': {
          50: '#f0f5ff',
          100: '#e0ebff',
          200: '#c7d7fe',
          300: '#a3bcfd',
          400: '#7a97fa',
          500: '#5472f6',
          600: '#3d52eb',
          700: '#2f3fd8',
          800: '#2935ae',
          900: '#273289',
          950: '#1a1f54',
        },
      },
    },
  },
  plugins: [],
}
