/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'gov-canvas': '#F8FAFC',
        'gov-surface': '#FFFFFF',
        'gov-surface-subtle': '#F1F5F9',
        'gov-border': '#E2E8F0',
        'gov-navy': '#0B3C5D',
        'nic-navy': '#0B3C5D',
        'gov-text-primary': '#0F172A',
        'gov-text-secondary': '#475569',
        'gov-text-muted': '#64748B',
        'severity-critical': '#D32F2F',
        'severity-severe': '#C2410C',
        'severity-advisory': '#B45309',
        'severity-normal': '#15803D',
        'tricolor-saffron': '#FF9933',
        'tricolor-green': '#138808',
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'Inter', '-apple-system', 'sans-serif'],
        mono: ['var(--font-mono)', 'JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};
