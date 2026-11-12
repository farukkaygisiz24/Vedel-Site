export function getServicePortalUrl() {
  if (process.env.NEXT_PUBLIC_SERVICE_URL) {
    return process.env.NEXT_PUBLIC_SERVICE_URL
  }
  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    if (host === 'localhost' || host === '127.0.0.1') {
      return 'http://localhost:8000'
    }
  }
  return 'https://servis.vedel.com.tr'
}
