/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./frontend/templates/**/*.{html,js}",
    "./frontend/src/**/*.{js,css}"
  ],
  theme: {
    extend: {
      maxWidth: {
        '7xl': '1200px',
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
}
