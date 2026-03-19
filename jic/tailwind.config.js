/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  safelist: [
    "bg-primary/90",
    "text-primary-foreground",
    "bg-secondary-foreground/65",
    "bg-amber-400",
    "text-secondary-foreground",
  ],
}
