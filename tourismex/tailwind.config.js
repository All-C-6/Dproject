/** @type {import('tailwindcss').Config} */

module.exports = {
    content: ['./templates/*.html', '.*.html'],
    darkMode: 'class',
    theme: {
      fontFamily: {
        'sans': ['Helvetica', 'Arial', 'sans-serif']
      },
        extend: {
            colors: {
                color_base: "#004953",
                color_graphit: "#2B2B2B",
                color_base_gray: "#2B2B2B",
                color_turquoise: "#5D9BC9",
                a1_color: "#018185",
                b1_color: "#292b2f",
                c1_color: "#018185",
                d1_color: "#292b2f",
            },
            padding: {
                standart: "10px",
                low: "6px",
                high: "18px",
            },
            margin: {
                standart: "40px",
                low: "24px",
            },
            font: {
              standart: "16px",
              head: "40px",
            }
        },
    },
    plugins: [
        require('tailwind-scrollbar')
        ],
}
