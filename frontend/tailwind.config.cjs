module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F19',
        accent: '#0086FF'
      },
      fontFamily: {
        sans: ['Oswald', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', 'serif']
      }
    }
  },
  plugins: []
}
