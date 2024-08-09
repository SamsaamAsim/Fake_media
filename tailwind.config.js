/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      './templates/**/*.{html,js}',
      './static/**/*.{html,js}',
    ],
    theme: {
        extend: {
            colors: {
              'custom-bg': '#F3E49B', // Add your custom color here
            },
          },
    },
    plugins: [
      require('flowbite/plugin')({
          charts: true,
      }),
      // ... other plugins
    ]
  }
  