import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'İletişim | VEDEL Klima',
  description: 'VEDEL Klima iletişim bilgileri. Kayapa ve Özlüce bayilerimiz. (0224) 413 23 16 - vedel@vedel.com.tr',
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
    address: 'Altınşehir Mah. Uğur Mumcu BLV. NO:58/E Nilüfer / Bursa',
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

const contactCardClassName =
  'flex items-center gap-4 rounded-2xl border border-white/20 bg-white/10 p-4 backdrop-blur-sm transition-colors active:bg-white/20 sm:flex-col sm:p-6 sm:text-center md:hover:bg-white/20'

export default function Iletisim() {
  return (
    <div className="min-h-screen bg-gray-50">

      <section className="relative overflow-hidden pt-20 pb-16 sm:pb-24 md:pb-32">
        <div className="absolute inset-0 bg-gradient-to-br from-red-900 via-red-800 to-red-900" />
        <div className="absolute inset-0 opacity-10">
          <div className="absolute left-4 top-20 h-48 w-48 rounded-full bg-white blur-3xl sm:left-10 sm:h-72 sm:w-72" />
          <div className="absolute bottom-6 right-4 h-56 w-56 rounded-full bg-red-400 blur-3xl sm:bottom-10 sm:right-20 sm:h-96 sm:w-96" />
        </div>

        <div className="container relative z-10 mx-auto px-4 sm:px-6">
          <div className="mx-auto max-w-4xl text-center">
            <h1 className="mb-4 text-3xl font-bold text-white sm:mb-6 sm:text-4xl md:text-6xl">
              İletişim
            </h1>
            <p className="mx-auto max-w-3xl text-base leading-relaxed text-red-100 sm:text-xl md:text-2xl">
              Sorularınız ve talepleriniz için bize ulaşın.
              Uzman ekibimiz en kısa sürede size yardımcı olacaktır.
            </p>
          </div>

          <div className="mt-10 grid grid-cols-1 gap-3 sm:mt-16 sm:gap-4 md:grid-cols-3 md:gap-8">
            <a href="tel:+902244132316" className={contactCardClassName}>
              <Phone className="h-7 w-7 shrink-0 text-red-300 sm:mx-auto sm:mb-3 sm:h-8 sm:w-8" />
              <div className="min-w-0 text-left sm:text-center">
                <div className="text-base font-bold text-white sm:text-lg md:text-xl">(0224) 413 23 16</div>
                <div className="text-sm text-red-200">7/24 Teknik Destek</div>
              </div>
            </a>
            <a href="mailto:vedel@vedel.com.tr" className={contactCardClassName}>
              <Mail className="h-7 w-7 shrink-0 text-red-300 sm:mx-auto sm:mb-3 sm:h-8 sm:w-8" />
              <div className="min-w-0 text-left sm:text-center">
                <div className="break-all text-sm font-bold text-white sm:break-normal sm:text-base md:text-xl">
                  vedel@vedel.com.tr
                </div>
                <div className="text-sm text-red-200">E-posta</div>
              </div>
            </a>
            <div className={contactCardClassName}>
              <Clock className="h-7 w-7 shrink-0 text-red-300 sm:mx-auto sm:mb-3 sm:h-8 sm:w-8" />
              <div className="min-w-0 text-left sm:text-center">
                <div className="text-base font-bold text-white sm:text-lg md:text-xl">09:00 - 18:00</div>
                <div className="text-sm text-red-200">Hafta İçi Çalışma Saatleri</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-12 sm:py-16 md:py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="mb-8 text-center sm:mb-12 md:mb-16">
            <h2 className="mb-3 text-2xl font-bold text-gray-900 sm:mb-4 sm:text-3xl md:text-4xl">
              Bayilerimiz
            </h2>
            <p className="mx-auto max-w-2xl px-2 text-sm text-gray-600 sm:px-0 sm:text-base">
              İki şubemiz ile Bursa&apos;da hizmetinizdeyiz. Size en yakın şubemizi
              ziyaret edebilir veya arayabilirsiniz.
            </p>
          </div>

          <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 sm:gap-8 md:grid-cols-2">
            {branches.map((branch, index) => (
              <div
                key={index}
                className="group overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-lg transition-all duration-300 md:hover:-translate-y-2 md:hover:border-red-200 md:hover:shadow-2xl"
              >
                <div className="p-5 sm:p-6 md:p-8">
                  <div className="mb-5 flex items-start gap-3 sm:mb-6 sm:items-center sm:gap-4">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-red-100 transition-colors duration-300 sm:h-12 sm:w-12 md:group-hover:bg-red-600">
                      <MapPin className="h-5 w-5 text-red-600 transition-colors duration-300 sm:h-6 sm:w-6 md:group-hover:text-white" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="text-lg font-bold text-gray-900 sm:text-xl">{branch.name}</h3>
                      <p className="text-sm text-gray-500">Vedel Klima Yetkili Bayi</p>
                    </div>
                  </div>

                  <div className="mb-5 rounded-xl bg-gray-50 p-4 transition-colors duration-300 sm:mb-6 md:group-hover:bg-red-50">
                    <div className="mb-2 flex items-center gap-3">
                      <User className="h-5 w-5 shrink-0 text-red-600" />
                      <span className="text-sm text-gray-500">Sorumlu:</span>
                    </div>
                    <div className="text-base font-bold text-gray-900 sm:text-lg">{branch.manager}</div>
                    <div className="mt-3">
                      <a
                        href={`tel:+9${branch.phone.replace(/\s/g, '')}`}
                        className="inline-flex min-h-11 items-center gap-2 rounded-lg py-1 text-base font-semibold text-green-600 active:text-green-700 sm:text-lg"
                      >
                        <Smartphone className="h-4 w-4 shrink-0" />
                        {branch.phone}
                      </a>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <MapPin className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
                    <p className="min-w-0 break-words text-sm text-gray-600 sm:text-base">{branch.address}</p>
                  </div>
                </div>

                <div className="h-48 w-full sm:h-56 md:h-64">
                  <iframe
                    src={branch.mapEmbed}
                    width="100%"
                    height="100%"
                    style={{ border: 0 }}
                    allowFullScreen
                    loading="lazy"
                    referrerPolicy="no-referrer-when-downgrade"
                    title={branch.name}
                    sandbox="allow-scripts allow-same-origin allow-popups"
                    className="h-full w-full"
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
