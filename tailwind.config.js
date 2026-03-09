/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./mysite/templates/**/*.html",
    "./mysite/**/templates/**/*.html",
    "./mysite/theme/templates/**/*.html",
    "./mysite/web/templates/**/*.html",
    "./mysite/**/templates/**/*.{html,js}",
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        // Colores personalizados para JIC
        'jic-primary': '#1e40af',
        'jic-secondary': '#0ea5e9',
        'jic-accent': '#f59e0b',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'heading': ['Poppins', 'sans-serif'],
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [
    require('flowbite/plugin'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}
