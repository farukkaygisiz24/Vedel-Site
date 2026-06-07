import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Multi Sistem Hesaplayıcı',
  description:
    'MHI multi split sistem fiyat hesaplayıcı. Dış ünite ve iç ünite seçerek tahmini sistem maliyetinizi hesaplayın.',
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://vedel.com.tr/urunler/multisistemler/mhi/hesaplayici',
    siteName: 'VEDEL Klima',
    title: 'Multi Sistem Hesaplayıcı | VEDEL Klima',
    description: 'MHI multi split sistem fiyat hesaplayıcı.',
  },
}

export default function HesaplayiciLayout({ children }: { children: React.ReactNode }) {
  return children
}
