/** @type {import('tailwindcss').Config} */
module.exports = {
    mode: 'jit',
    content: ['./templates/*.html', './static/*.{html,js}'],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                a-color: "#018185",
                b-color: "#292b2f",
                c-color: "#393b3f",
                d-color: "#3bbfc3",
                a1-color: "#018185",
                b1-color: "#292b2f",
                c1-color: "#018185",
                d1-color: "#292b2f",
            },
            padding: {
                standart: 10px,
                low: 6px,
                high: 18px,
            },
            margin: {
                standart: 10px,
                low: 6px,
                high: 18px,
            },
        },
    },
    plugins: [],
}
