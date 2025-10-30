/**
 * Get the API base URL dynamically based on the current environment
 *
 * This utility ensures API calls work when accessing the app via:
 * - localhost (http://localhost:PORT)
 * - Network IP (http://192.168.1.100:PORT)
 * - Domain name (http://example.com)
 * - Windows server IP address
 *
 * The backend port is read from NEXT_PUBLIC_BACKEND_PORT environment variable,
 * which should be set in .env file (defaults to 8000 if not set).
 *
 * @returns The base URL for API calls (e.g., "http://192.168.1.100:8501")
 */
export function getApiBaseUrl(): string {
  // Client-side: use current browser hostname with configured backend port
  if (typeof window !== 'undefined') {
    console.log('[API-URL] Client-side URL generation');
    console.log('[API-URL] Environment variables:', {
      NEXT_PUBLIC_BACKEND_PORT: process.env.NEXT_PUBLIC_BACKEND_PORT,
      NODE_ENV: process.env.NODE_ENV
    });

    // Get backend port with proper validation
    const envPort = process.env.NEXT_PUBLIC_BACKEND_PORT;
    console.log('[API-URL] Raw NEXT_PUBLIC_BACKEND_PORT:', envPort);

    // Parse and validate the port
    let backendPort = '8000'; // Default
    if (envPort) {
      const parsedPort = parseInt(envPort.trim(), 10);
      if (!isNaN(parsedPort) && parsedPort > 0 && parsedPort <= 65535) {
        backendPort = String(parsedPort);
        console.log('[API-URL] Using configured port:', backendPort);
      } else {
        console.warn('[API-URL] Invalid NEXT_PUBLIC_BACKEND_PORT:', envPort, '- using default 8000');
      }
    } else {
      console.log('[API-URL] NEXT_PUBLIC_BACKEND_PORT not set, using default:', backendPort);
    }

    const hostname = window.location.hostname;
    const protocol = window.location.protocol.includes('https') ? 'https' : 'http';
    const baseUrl = `${protocol}://${hostname}:${backendPort}`;

    console.log('[API-URL] Window location:', {
      hostname,
      protocol,
      port: window.location.port,
      href: window.location.href
    });
    console.log('[API-URL] Generated base URL:', baseUrl);

    // Validate the URL
    try {
      const testUrl = new URL(baseUrl);
      console.log('[API-URL] URL validation passed:', testUrl.toString());
      return baseUrl;
    } catch (error) {
      console.error('[API-URL] Invalid URL generated:', baseUrl, error);
      // Fallback to localhost
      const fallbackUrl = `http://localhost:${backendPort}`;
      console.warn('[API-URL] Using fallback URL:', fallbackUrl);
      return fallbackUrl;
    }
  }

  // Server-side: use localhost for SSR/build time
  const port = process.env.NEXT_PUBLIC_BACKEND_PORT || '8000';
  const serverUrl = `http://localhost:${port}`;
  console.log('[API-URL] Server-side URL:', serverUrl);
  return serverUrl;
}
