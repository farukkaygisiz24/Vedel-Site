import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'İletişim | VEDEL Klima',
  description: 'VEDEL Klima iletişim bilgileri. Kayapa ve Özlüce bayilerimiz. (0224) 413 16 17 - vedel@vedel.com.tr',
  keywords: ['klima iletişim', 'vedel iletişim', 'bursa klima bayii', 'mhi servis', 'euroform servis'],
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://vedel.com.tr/iletisim',
    siteName: 'VEDEL Klima',
    title: 'İletişim | VEDEL Klima',
    description: 'VEDEL Klima iletişim bilgileri. Kayapa ve Özlüce bayilerimiz.',
    images: [
      {
        url: '/vedel-logo.png',
        width: 1200,
        height: 630,
        alt: 'VEDEL Klima - İletişim',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'İletişim | VEDEL Klima',
    description: 'VEDEL Klima iletişim bilgileri. Kayapa ve Özlüce bayilerimiz.',
    images: ['/vedel-logo.png'],
  },
}

import {
  Phone,
  Mail,
  MapPin,
  Clock,
  User,
  Smartphone
} from 'lucide-react'

const branches = [
  {
    name: 'Özlüce Bayi',
    manager: 'Ömer Faruk',
    phone: '0554 571 69 84',
    address: 'Altınşehir Mah. Uğur Mumcu BLV. NO:58/E Nilüfer Bursa',
    mapEmbed: 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d24375.88875737446!2d28.877606499362837!3d40.20937226027395!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x14ca11dbd805d031%3A0x53d5fb061d1115ae!2sVedel%20Klima%20-%20Mitsubishi!5e0!3m2!1str!2str!4v1745509265743!5m2!1str!2str'
  },
  {
    name: 'Kayapa Bayi',
    manager: 'Kerem Ferik',
    phone: '0535 238 16 53',
    address: '30 Ağustos Zafer Mah. Bozyaka Cad. NO:11/CA Nilüfer / Bursa',
    mapEmbed: 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d24378.8590020303!2d28.834176170993697!3d40.20111269950986!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x14ca0f8d493aab77%3A0x4a30d270907bf624!2sVedel%20Klima%20-%20Mitsubishi!5e0!3m2!1str!2str!4v1745509235544!5m2!1str!2str'
  }
]

export default function Iletisim() {
  return (
    <div className="min-h-screen bg-gray-50">

      <section className="relative pt-20 pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-red-900 via-red-800 to-red-900" />
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-20 w-96 h-96 bg-red-400 rounded-full blur-3xl" />
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              İletişim
            </h1>
            <p className="text-xl md:text-2xl text-red-100 leading-relaxed max-w-3xl mx-auto">
              Sorularınız ve talepleriniz için bize ulaşın.
              Uzman ekibimiz en kısa sürede size yardımcı olacaktır.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-8 mt-16">
            <a
              href="tel:+902244131617"
              className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center border border-white/20 hover:bg-white/20 transition-colors"
            >
              <Phone className="w-8 h-8 text-red-300 mx-auto mb-3" />
              <div className="text-base md:text-xl font-bold text-white mb-1">(0224) 413 16 17</div>
              <div className="text-red-200 text-sm">7/24 Teknik Destek</div>
            </a>
            <a
              href="mailto:vedel@vedel.com.tr"
              className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center border border-white/20 hover:bg-white/20 transition-colors"
            >
              <Mail className="w-8 h-8 text-red-300 mx-auto mb-3" />
              <div className="text-sm sm:text-base md:text-xl font-bold text-white mb-1 break-words">vedel@vedel.com.tr</div>
              <div className="text-red-200 text-sm">E-posta</div>
            </a>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center border border-white/20">
              <Clock className="w-8 h-8 text-red-300 mx-auto mb-3" />
              <div className="text-base md:text-xl font-bold text-white mb-1">09:00 - 18:00</div>
              <div className="text-red-200 text-sm">Hafta İçi Çalışma Saatleri</div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Bayilerimiz
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              İki şubemiz ile Bursa&apos;da hizmetinizdeyiz. Size en yakın şubemizi
              ziyaret edebilir veya arayabilirsiniz.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            {branches.map((branch, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl overflow-hidden shadow-lg border border-gray-100 hover:shadow-xl transition-shadow"
              >
                <div className="p-8">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                        <MapPin className="w-6 h-6 text-red-600" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">{branch.name}</h3>
                        <p className="text-gray-500 text-sm">Vedel Klima Yetkili Bayi</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-xl p-4 mb-6">
                    <div className="flex items-center gap-3 mb-2">
                      <User className="w-5 h-5 text-red-600" />
                      <span className="text-sm text-gray-500">Sorumlu:</span>
                    </div>
                    <div className="font-bold text-gray-900 text-lg">{branch.manager}</div>
                    <div className="flex items-center gap-2 mt-3">
                      <Smartphone className="w-4 h-4 text-green-600" />
                      <a
                        href={`tel:+9${branch.phone.replace(/\s/g, '')}`}
                        className="text-green-600 font-semibold hover:underline"
                      >
                        {branch.phone}
                      </a>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 mb-6">
                    <MapPin className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-gray-600">{branch.address}</p>
                  </div>
                </div>

                <div className="h-64 w-full">
                  <iframe
                    src={branch.mapEmbed}
                    width="100%"
                    height="100%"
                    style={{ border: 0 }}
                    allowFullScreen
                    loading="lazy"
                    referrerPolicy="no-referrer-when-downgrade"
                    title={branch.name}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>


    </div>
  )
}
