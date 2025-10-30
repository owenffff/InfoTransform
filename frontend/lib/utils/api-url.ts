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
    const backendPort = process.env.NEXT_PUBLIC_BACKEND_PORT || '8000';
    const hostname = window.location.hostname;
    return `http://${hostname}:${backendPort}`;
  }

  // Server-side: use localhost for SSR/build time
  return `http://localhost:${process.env.NEXT_PUBLIC_BACKEND_PORT || 8000}`;
}
