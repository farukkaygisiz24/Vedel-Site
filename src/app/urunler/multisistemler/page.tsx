import type { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, Snowflake, Wind, Flame, Zap, Layers } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Multi Sistem Klimalar | Tek Dış Ünite Birden Fazla İç Ünite',
  description: 'Multi sistem klimalar. Tek dış üniteye birden fazla iç ünite bağlayın. MHI ve Euroform multi split klimalar. Ev ve işyeri için ideal çözüm.',
  keywords: ['multi klima', 'multi split klima', 'bir dış ünite birden fazla iç ünite', 'mhi multi', 'euroform multi'],
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://vedel.com.tr/urunler/multisistemler',
    siteName: 'VEDEL Klima',
    title: 'Multi Sistem Klimalar | VEDEL Klima',
    description: 'Multi sistem klimalar. Tek dış üniteye birden fazla iç ünite bağlayın. MHI ve Euroform multi split klimalar.',
    images: [
      {
        url: '/vedel-logo.png',
        width: 1200,
        height: 630,
        alt: 'VEDEL - Multi Sistem Klimalar',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Multi Sistem Klimalar | VEDEL Klima',
    description: 'Multi sistem klimalar. Tek dış üniteye birden fazla iç ünite bağlayın.',
    images: ['/vedel-logo.png'],
  },
}

export default function MultiSistemlerPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      <div className="relative bg-gradient-to-r from-purple-700 via-purple-600 to-indigo-800 py-16 md:py-24 overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-30"></div>

        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/20 rounded-full translate-y-1/2 -translate-x-1/2 blur-3xl"></div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="flex flex-col items-center text-center gap-8">
            <div className="max-w-2xl">
              <div className="flex items-center justify-center gap-3 mb-4">
                <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/20 rounded-full text-white text-sm font-medium">
                  <Layers className="w-4 h-4" />
                  Multi Split Sistemler
                </span>
              </div>
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4">
                Tek Dış Ünite, Birden Fazla İç Ünite
              </h1>
              <div className="overflow-hidden">
                <p className="text-white/90 text-lg animate-pulse">
                  Birden fazla odayı tek dış ünite ile soğutun veya ısıtın.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-white/80">
                <Snowflake className="w-5 h-5" />
                <span className="text-sm">Soğutma</span>
              </div>
              <div className="flex items-center gap-2 text-white/80">
                <Flame className="w-5 h-5" />
                <span className="text-sm">Isıtma</span>
              </div>
              <div className="flex items-center gap-2 text-white/80">
                <Wind className="w-5 h-5" />
                <span className="text-sm">Havalandırma</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12 md:py-16">
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <Link
            href="/urunler/multisistemler/mhi"
            className="group relative bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-2xl hover:-translate-y-2 transition-all duration-500"
          >
            <div className="absolute top-0 right-0 w-full h-32 bg-gradient-to-b from-purple-50 to-transparent"></div>

            <div className="p-8">
              <div className="relative w-32 h-16 mb-6">
                <Image
                  src="/mhi-logo.png"
                  alt="Mitsubishi Heavy Industries"
                  fill
                  className="object-contain"
                />
              </div>

              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  Mitsubishi Heavy Industries
                </h2>
                <div className="flex items-center bg-purple-50 text-purple-600 px-4 py-1 rounded-full border border-purple-100 text-sm font-medium">
                  <Zap className="w-3 h-3" />
                  Premium
                </div>
              </div>

              <p className="text-gray-600 mb-6 leading-relaxed">
                Japonya&apos;nın lider klima üreticisi MHI, yüksek kapasiteli multi sistemleri ile
                birden fazla odayı tek bir dış ünite ile iklimlendirmenizi sağlar.
              </p>

              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center">
                    <Zap className="w-4 h-4 text-green-600" />
                  </div>
                  <span>5 üniteye kadar bağlama</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                    <Wind className="w-4 h-4 text-blue-600" />
                  </div>
                  <span>Akıllı inverter teknolojisi</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center">
                    <Snowflake className="w-4 h-4 text-purple-600" />
                  </div>
                  <span>Bağımsız kontrol</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-cyan-50 flex items-center justify-center">
                    <Layers className="w-4 h-4 text-cyan-600" />
                  </div>
                  <span>Enerji tasarrufu</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <span className="text-sm text-gray-500">5 üniteye kadar</span>
                <div className="flex items-center gap-2 text-purple-600 font-semibold group-hover:gap-3 transition-all">
                  Ürünleri İncele
                  <ArrowRight className="w-5 h-5" />
                </div>
              </div>
            </div>
          </Link>

          <Link
            href="/urunler/multisistemler/euroform"
            className="group relative bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-2xl hover:-translate-y-2 transition-all duration-500"
          >
            <div className="absolute top-0 right-0 w-full h-32 bg-gradient-to-b from-blue-50 to-transparent"></div>

            <div className="p-8">
              <div className="relative w-32 h-16 mb-6">
                <Image
                  src="/euroform.png"
                  alt="Euroform"
                  fill
                  className="object-contain"
                />
              </div>

              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  Euroform
                </h2>
                <div className="flex items-center bg-blue-50 text-blue-600 px-4 py-1 rounded-full border border-blue-100 text-sm font-medium">
                  <Zap className="w-3 h-3" />
                  Ekonomik
                </div>
              </div>

              <p className="text-gray-600 mb-6 leading-relaxed">
                Türkiye&apos;nin yerli markası Euroform, uygun fiyatlı multi split sistemleri ile
                ev ve işyerlerinizde ekonomik çözümler sunar.
              </p>

              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center">
                    <Zap className="w-4 h-4 text-green-600" />
                  </div>
                  <span>Türkiye&apos;nin yerli markası</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                    <Wind className="w-4 h-4 text-blue-600" />
                  </div>
                  <span>Uygun fiyat performans</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center">
                    <Snowflake className="w-4 h-4 text-purple-600" />
                  </div>
                  <span>Yaygın servis ağı</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-cyan-50 flex items-center justify-center">
                    <Layers className="w-4 h-4 text-cyan-600" />
                  </div>
                  <span>Kolay yedek parça temini</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <span className="text-sm text-gray-500">5 üniteye kadar</span>
                <div className="flex items-center gap-2 text-blue-600 font-semibold group-hover:gap-3 transition-all">
                  Ürünleri İncele
                  <ArrowRight className="w-5 h-5" />
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* Hesaplama CTA */}
        <div className="mt-16 max-w-3xl mx-auto">
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-8 text-center">
            <h3 className="text-2xl font-bold text-white mb-3">
              İhtiyacınız Kadar İç Ünite
            </h3>
            <p className="text-white/80 mb-6">
              Kaç adet iç üniteye ihtiyacınız olduğunu hesaplayalım.
            </p>
            <Link
              href="/urunler/multisistemler/mhi/hesaplayici"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-purple-700 font-semibold rounded-xl hover:bg-purple-50 transition-colors"
            >
              <Layers className="w-5 h-5" />
              Multi Hesaplayıcı
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}
