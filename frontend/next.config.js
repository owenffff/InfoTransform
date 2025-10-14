/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  async rewrites() {
    // Read from NEXT_PUBLIC_BACKEND_PORT first (available at runtime),
    // fallback to BACKEND_PORT (build time), then default to 8000
    const backendPort = process.env.NEXT_PUBLIC_BACKEND_PORT || process.env.BACKEND_PORT || '8000';
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || `http://localhost:${backendPort}`;
    
    console.log(`[Next.js] API rewrites configured to: ${apiUrl}`);
    
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
  
  // Expose environment variables to the client
  env: {
    NEXT_PUBLIC_BACKEND_PORT: process.env.NEXT_PUBLIC_BACKEND_PORT || process.env.BACKEND_PORT || '8000',
  },
};

module.exports = nextConfig;
