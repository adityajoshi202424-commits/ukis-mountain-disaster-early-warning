/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Only proxy to the Python backend during LOCAL development.
  // On Vercel (production), the Next.js API routes in /src/app/api/ handle
  // everything — calling Open-Meteo, USGS, etc. directly from serverless functions.
  async rewrites() {
    if (process.env.VERCEL || process.env.NODE_ENV === 'production') {
      return []; // No rewrites in cloud — self-contained API routes serve all data
    }
    return {
      fallback: [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/api/:path*',
        },
        {
          source: '/sih-demo',
          destination: 'http://localhost:8000/sih-demo',
        },
      ],
    };
  },
};

module.exports = nextConfig;
