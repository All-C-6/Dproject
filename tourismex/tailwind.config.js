/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ['./templates/*.html', '.*.html'],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                base_color: "#004953",
                graphit_color: "#23282b",
                base_gray_color: "#393b3f",
                turquoise_dark_color: "#3bbfc3",
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
        },
    },
    plugins: [],
}
