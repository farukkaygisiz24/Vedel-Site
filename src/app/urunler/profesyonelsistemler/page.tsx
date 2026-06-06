import type { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, Snowflake, Wind, Flame, Zap, Building2, Factory } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Profesyonel Klima Sistemleri | Ticari İklimlendirme',
  description: 'Profesyonel klima sistemleri. Kaset tipi, kanal tipi, tavan tipi klimalar. MHI ve Euroform profesyonel çözümler. Otel, ofis, mağaza için.',
  keywords: ['profesyonel klima', 'ticari klima', 'kaset tipi klima', 'kanal tipi klima', 'tavan tipi klima', 'endüstriyel klima'],
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://vedel.com.tr/urunler/profesyonelsistemler',
    siteName: 'VEDEL Klima',
    title: 'Profesyonel Klima Sistemleri | VEDEL Klima',
    description: 'Profesyonel klima sistemleri. Kaset tipi, kanal tipi, tavan tipi klimalar. MHI ve Euroform profesyonel çözümler.',
    images: [
      {
        url: '/vedel-logo.png',
        width: 1200,
        height: 630,
        alt: 'VEDEL Profesyonel Klima Sistemleri',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Profesyonel Klima Sistemleri | VEDEL Klima',
    description: 'Profesyonel klima sistemleri. Kaset tipi, kanal tipi, tavan tipi klimalar.',
    images: ['/vedel-logo.png'],
  },
}

export default function ProfesyonelSistemlerPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      <div className="relative bg-gradient-to-r from-orange-700 via-orange-600 to-amber-700 py-16 md:py-24 overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-30"></div>

        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-orange-500/20 rounded-full translate-y-1/2 -translate-x-1/2 blur-3xl"></div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="flex flex-col items-center text-center gap-8">
            <div className="max-w-2xl">
              <div className="flex items-center justify-center gap-3 mb-4">
                <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/20 rounded-full text-white text-sm font-medium">
                  <Factory className="w-4 h-4" />
                  Profesyonel Klima Sistemleri
                </span>
              </div>
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4">
                Ticari & Endüstriyel Çözümler
              </h1>
              <div className="overflow-hidden">
                <p className="text-white/90 text-lg animate-pulse">
                  Mağazalardan fabrikalara, ofislerden depolara kadar her mekanda yüksek kapasiteli iklimlendirme.
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
        {/* Sistem Türleri */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Profesyonel Sistem Tipleri
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center mb-3">
                <Building2 className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-1">Kaset Tipi</h3>
              <p className="text-sm text-gray-500">4 yöne hava dağıtımı, tavan montaj</p>
            </div>
            <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center mb-3">
                <Wind className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-1">Kanal Tipi</h3>
              <p className="text-sm text-gray-500">Gizli montaj, ortam havalandırması</p>
            </div>
            <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center mb-3">
                <Factory className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-1">Salon Tipi</h3>
              <p className="text-sm text-gray-500">Yüksek kapasite, geniş alanlar</p>
            </div>
            <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center mb-3">
                <Flame className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-1">Tavan Tipi</h3>
              <p className="text-sm text-gray-500">Tavan tipi montaj, Endüstriyel</p>
            </div>
          </div>
        </div>

        {/* Marka Kartları */}
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <Link
            href="/urunler/profesyonelsistemler/mhi"
            className="group relative bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-2xl hover:-translate-y-2 transition-all duration-500"
          >
            <div className="absolute top-0 right-0 w-full h-32 bg-gradient-to-b from-orange-50 to-transparent"></div>

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
                <div className="flex items-center bg-orange-50 text-orange-600 px-4 py-1 rounded-full border border-orange-100 text-sm font-medium">
                  <Zap className="w-3 h-3" />
                  Premium
                </div>
              </div>

              <p className="text-gray-600 mb-6 leading-relaxed">
                Japonya&apos;nın lider üreticisi MHI, yüksek kapasiteli profesyonel sistemleri ile
                ticari ve endüstriyel alanlarda güvenilir iklimlendirme çözümleri sunar.
              </p>

              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center">
                    <Zap className="w-4 h-4 text-green-600" />
                  </div>
                  <span>24.000 - 85.000 BTU kapasite</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                    <Wind className="w-4 h-4 text-blue-600" />
                  </div>
                  <span>Yüksek verimlilik</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-orange-50 flex items-center justify-center">
                    <Building2 className="w-4 h-4 text-orange-600" />
                  </div>
                  <span>Ticari & endüstriyel kullanım</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-lg bg-cyan-50 flex items-center justify-center">
                    <Snowflake className="w-4 h-4 text-cyan-600" />
                  </div>
                  <span>Uzun ömürlü performans</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <span className="text-sm text-gray-500">Kaset, Kanal, Salon, Tavan</span>
                <div className="flex items-center gap-2 text-orange-600 font-semibold group-hover:gap-3 transition-all">
                  Ürünleri İncele
                  <ArrowRight className="w-5 h-5" />
                </div>
              </div>
            </div>
          </Link>

          <Link
            href="/urunler/profesyonelsistemler/euroform"
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
                Türkiye&apos;nin yerli markası Euroform, uygun fiyatlı profesyonel sistemleri ile
                işletmelerinizde ekonomik ve güvenilir iklimlendirme sağlar.
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
                    <Building2 className="w-4 h-4 text-cyan-600" />
                  </div>
                  <span>Kolay yedek parça temini</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <span className="text-sm text-gray-500">Kaset, Kanal, Tavan</span>
                <div className="flex items-center gap-2 text-blue-600 font-semibold group-hover:gap-3 transition-all">
                  Ürünleri İncele
                  <ArrowRight className="w-5 h-5" />
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* Kapasite Bilgisi */}
        <div className="mt-16 max-w-4xl mx-auto">
          <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-2xl p-8 border border-orange-100">
            <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">
              Hangi Kapasiteyi Seçmeliyim?
            </h3>
            <div className="grid sm:grid-cols-3 gap-4">
              <div className="bg-white rounded-xl p-4 border border-orange-100">
                <div className="text-2xl font-bold text-orange-600 mb-1">24.000 BTU</div>
                <div className="text-sm text-gray-600">SmallOfis / Küçük Dükkan</div>
                <div className="text-xs text-gray-400 mt-1">~50-80 m²</div>
              </div>
              <div className="bg-white rounded-xl p-4 border border-orange-100">
                <div className="text-2xl font-bold text-orange-600 mb-1">42.000 BTU</div>
                <div className="text-sm text-gray-600">Orta Büyüklükte İşyeri</div>
                <div className="text-xs text-gray-400 mt-1">~80-130 m²</div>
              </div>
              <div className="bg-white rounded-xl p-4 border border-orange-100">
                <div className="text-2xl font-bold text-orange-600 mb-1">85.000 BTU</div>
                <div className="text-sm text-gray-600">Büyük Endüstriyel Alan</div>
                <div className="text-xs text-gray-400 mt-1">~150-250 m²</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
