import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  async redirects() {
    return [
      { source: '/hakkinda.html', destination: '/hakkimizda', permanent: true },
      { source: '/iletisim.html', destination: '/iletisim', permanent: true },
      { source: '/hizmettalepformu.html', destination: '/iletisim', permanent: true },
      { source: '/gizlilikpolitikasi.html', destination: '/', permanent: true },
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
