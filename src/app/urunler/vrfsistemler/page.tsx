import type { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'
import { 
  ArrowRight, Snowflake, Wind, Flame, Zap, 
  Building2, Cpu, Gauge, Leaf, Shield,
  ArrowUpRight, Info, CheckCircle2
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'VRF Sistemler | Variable Refrigerant Flow',
  description: 'VRF sistemler. Değişken soğutucu akışkan miktarı teknolojisi. MHI VRF klimalar. Büyük bina, otel, AVM için ideal çözüm.',
  keywords: ['vrf klima', 'vrf sistem', 'variable refrigerant flow', 'mhi vrf', 'merkezi klima', 'büyük bina klima'],
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://vedel.com.tr/urunler/vrfsistemler',
    siteName: 'VEDEL Klima',
    title: 'VRF Sistemler | VEDEL Klima',
    description: 'VRF sistemler. Değişken soğutucu akışkan miktarı teknolojisi. MHI VRF klimalar. Büyük bina, otel, AVM için ideal çözüm.',
    images: [
      {
        url: '/vedel-logo.png',
        width: 1200,
        height: 630,
        alt: 'VEDEL VRF Sistemler',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VRF Sistemler | VEDEL Klima',
    description: 'VRF sistemler. Değişken soğutucu akışkan miktarı teknolojisi. MHI VRF klimalar.',
    images: ['/vedel-logo.png'],
  },
}

export default function VRFSistemlerPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      {/* Header */}
      <div className="relative bg-gradient-to-r from-teal-700 via-teal-600 to-emerald-700 py-16 md:py-24 overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-30"></div>

        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-teal-500/20 rounded-full translate-y-1/2 -translate-x-1/2 blur-3xl"></div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="flex flex-col items-center text-center gap-8">
            <div className="max-w-2xl">
              <div className="flex items-center justify-center gap-3 mb-4">
                <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/20 rounded-full text-white text-sm font-medium">
                  <Building2 className="w-4 h-4" />
                  VRF Sistemleri
                </span>
              </div>
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4">
                Değişken Soğutucu Akışkan Debisi
              </h1>
              <div className="overflow-hidden">
                <p className="text-white/90 text-lg animate-pulse">
                  Enerji verimli, esnek ve akıllı iklimlendirme çözümleri
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
        {/* VRF Nedir? */}
        <div className="max-w-4xl mx-auto mb-16">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-teal-600 to-emerald-600 px-8 py-6">
              <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                <Info className="w-6 h-6" />
                VRF Sistemi Nedir?
              </h2>
            </div>
            <div className="p-8">
              <p className="text-gray-700 text-lg leading-relaxed mb-8">
                <strong>VRF (Variable Refrigerant Flow)</strong> veya Türkçe adıyla 
                <strong> Değişken Soğutucu Akışkan Debili</strong> sistemler, 
                merkezi iklime sistemlerinin en gelişmiş versiyonudur. Tek bir dış üniteye 
                bağlı birden fazla iç ünite ile her odayı ayrı ayrı kontrol edebilir, 
                enerji tasarrufu sağlayabilirsiniz.
              </p>
              
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="bg-teal-50 rounded-xl p-5 border border-teal-100">
                  <div className="flex items-center gap-3 mb-2">
                    <Gauge className="w-5 h-5 text-teal-600" />
                    <h3 className="font-bold text-teal-800">Akıllı Kapasite Ayarı</h3>
                  </div>
                  <p className="text-sm text-teal-700">
                    İhtiyaca göre soğutma/ısıtma kapasitesini otomatik ayarlar
                  </p>
                </div>
                <div className="bg-teal-50 rounded-xl p-5 border border-teal-100">
                  <div className="flex items-center gap-3 mb-2">
                    <Leaf className="w-5 h-5 text-teal-600" />
                    <h3 className="font-bold text-teal-800">Yüksek Enerji Verimi</h3>
                  </div>
                  <p className="text-sm text-teal-700">
                    Geleneksel sistemlere göre %40&apos;a varan enerji tasarrufu
                  </p>
                </div>
                <div className="bg-teal-50 rounded-xl p-5 border border-teal-100">
                  <div className="flex items-center gap-3 mb-2">
                    <Cpu className="w-5 h-5 text-teal-600" />
                    <h3 className="font-bold text-teal-800">Bağımsız Kontrol</h3>
                  </div>
                  <p className="text-sm text-teal-700">
                    Her iç ünite ayrı ayrı sıcaklık ve mod ayarı yapılabilir
                  </p>
                </div>
                <div className="bg-teal-50 rounded-xl p-5 border border-teal-100">
                  <div className="flex items-center gap-3 mb-2">
                    <Building2 className="w-5 h-5 text-teal-600" />
                    <h3 className="font-bold text-teal-800">Geniş Kapasite</h3>
                  </div>
                  <p className="text-sm text-teal-700">
                    8 ila 64+ iç üniteye kadar bağlama imkanı
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Neden 2VKlima? */}
        <div className="max-w-4xl mx-auto mb-16">
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-8 md:p-12 text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-4">
              Neden 2VKlima?
            </h2>
            <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
              VRF sistemler konusunda uzman kadromuz ve Mitsubishi Heavy Industries 
              güvencesiyle en doğru çözümü sunuyoruz. Proje danışmanlığından 
              montajına kadar profesyonel hizmet.
            </p>
            
            <div className="grid sm:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <div className="w-12 h-12 bg-teal-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CheckCircle2 className="w-6 h-6 text-teal-400" />
                </div>
                <h3 className="font-bold text-white mb-1">Uzman Kadro</h3>
                <p className="text-sm text-gray-400">VRF sertifikalı teknisyenler</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-teal-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Shield className="w-6 h-6 text-teal-400" />
                </div>
                <h3 className="font-bold text-white mb-1">MHI Garantisi</h3>
                <p className="text-sm text-gray-400">Orijinal Mitsubishi Heavy</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-teal-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Zap className="w-6 h-6 text-teal-400" />
                </div>
                <h3 className="font-bold text-white mb-1">7/24 Destek</h3>
                <p className="text-sm text-gray-400">Satış sonrası teknik servis</p>
              </div>
            </div>

            {/* Yönlendirme Kartı */}
            <a
              href="https://2vklima.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="group inline-flex items-center gap-3 px-8 py-4 bg-teal-500 text-white font-bold rounded-xl hover:bg-teal-400 transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              <span>2VKlima.com&apos;da VRF Ürünlerini İncele</span>
              <ArrowUpRight className="w-5 h-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
            </a>
            <p className="text-sm text-gray-500 mt-4">
              Açılan sayfa 2VKlima.com&apos;a yönlendirecek
            </p>
          </div>
        </div>

        {/* MHI Logo & Bilgi */}
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 md:p-12 text-center">
            <div className="relative w-48 h-20 mx-auto mb-6">
              <Image
                src="/mhi-logo.png"
                alt="Mitsubishi Heavy Industries"
                fill
                className="object-contain"
              />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              Dünya Markası: Mitsubishi Heavy Industries
            </h3>
            <p className="text-gray-600 leading-relaxed">
              VRF sistemlerde dünya lideri Mitsubishi Heavy Industries, 
              yüzlerce bina ve tesiste kanıtlanmış güvenilirlik sunar. 
              Japon kalitesi ve ileri teknolojisi ile en zorlu iklimlendirme 
              ihtiyaçlarınızı karşılayın.
            </p>
            <div className="flex items-center justify-center gap-8 mt-6 pt-6 border-t border-gray-100">
              <div className="text-center">
                <div className="text-2xl font-bold text-teal-600">85.000+</div>
                <div className="text-sm text-gray-500">Kurulum</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-teal-600">%40</div>
                <div className="text-sm text-gray-500">Enerji Tasarrufu</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-teal-600">20+</div>
                <div className="text-sm text-gray-500">Yıl Ömür</div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 max-w-2xl mx-auto text-center">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            VRF Projeniz İçin Yardım Alın
          </h3>
          <p className="text-gray-600 mb-6">
            İşyeri veya konut projeniz için VRF sistemi uygun mu? 
            Kapasite hesabı ve fiyat teklifi için uzmanlarımızla görüşün.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/iletisim"
              className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 text-white font-semibold rounded-xl hover:bg-teal-700 transition-colors"
            >
              İletişime Geç
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="tel:02244131617"
              className="inline-flex items-center gap-2 px-6 py-3 border-2 border-teal-600 text-teal-600 font-semibold rounded-xl hover:bg-teal-50 transition-colors"
            >
              (0224) 413 16 17
            </a>
          </div>
        </div>
      </div>
    </main>
  )
}
