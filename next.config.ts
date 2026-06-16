import type { NextConfig } from "next";

const securityHeaders = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-XSS-Protection', value: '1; mode=block' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=(), payment=()' },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
]

const nextConfig: NextConfig = {
  output: 'standalone',
  productionBrowserSourceMaps: false,
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },
  images: {
    qualities: [75, 90, 100],
    localPatterns: [
      { pathname: '/MHI/**' },
      { pathname: '/euroform/**' },
      { pathname: '/**' },
    ],
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ]
  },
  async redirects() {
    return [
      { source: '/hakkinda.html', destination: '/hakkimizda', permanent: true },
      { source: '/iletisim.html', destination: '/iletisim', permanent: true },
      { source: '/hizmettalepformu.html', destination: '/iletisim', permanent: true },
      { source: '/gizlilikpolitikasi.html', destination: '/gizlilik-politikasi', permanent: true },
      { source: '/campaign/mhi-yaz-kampanya.mp4', destination: '/', permanent: true },
      { source: '/split-klimalar.html', destination: '/urunler/splitsistemler/mhi', permanent: true },
      { source: '/multi-split-klimalar.html', destination: '/urunler/multisistemler/mhi', permanent: true },
      { source: '/profesyonel-klimalar.html', destination: '/urunler/profesyonelsistemler/mhi', permanent: true },
      { source: '/euroform/profesyonel-seri/:path*', destination: '/urunler/profesyonelsistemler/euroform', permanent: true },
      { source: '/mitsubishiheavyindustries/splitklimalar/:path*', destination: '/urunler/splitsistemler/mhi', permanent: true },
      { source: '/mitsubishiheavyindustries/multi-sistemler/:path*', destination: '/urunler/multisistemler/mhi', permanent: true },
      { source: '/mitsubishiheavyindustries/profesyonel-seri/:path*', destination: '/urunler/profesyonelsistemler/mhi', permanent: true },
      { source: '/mitsubishiheavyindustries/:path*', destination: '/urunler/splitsistemler/mhi', permanent: true }
    ]
  }
};

export default nextConfig;
