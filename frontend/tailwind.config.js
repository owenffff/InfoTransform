/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      maxWidth: {
        '7xl': '1200px',
      },
      fontFamily: {
        'sans': ['Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
      },
      colors: {
        // Brand Orange Colors
        'brand-orange': {
          50: '#FFF5ED',
          100: '#FFE8D4',
          200: '#FFCDA8',
          300: '#FFAA72',
          400: '#FE7C39',
          500: '#FD5108', // Core brand orange
          600: '#E8460A', // Darker orange for hover states
          700: '#D13D09', // Even darker orange for text
        },
        // Brand Gray Colors
        'brand-gray': {
          50: '#F5F7F8',
          100: '#EEEFF1',
          200: '#DFE3E6',
          300: '#CBD1D6',
          400: '#B5BCC4',
          500: '#A1A8B3',
        },
      },
      animation: {
        'spin': 'spin 1s linear infinite',
        'fadeIn': 'fadeIn 0.3s ease-in',
      },
      keyframes: {
        fadeIn: {
          'from': { opacity: '0', transform: 'translateY(-10px)' },
          'to': { opacity: '1', transform: 'translateY(0)' }
        }
      }
    },
  },
  plugins: [],
};