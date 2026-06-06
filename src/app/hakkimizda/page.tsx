import type { Metadata } from 'next'
import Image from 'next/image'

export const metadata: Metadata = {
  title: 'Hakkımızda | VEDEL Klima',
  description: 'VEDEL Klima olarak 25 yılı aşkın süredir iklimlendirme sektöründe hizmet veriyoruz. MHI ve Euroform yetkili bayisi olarak profesyonel klima çözümleri sunuyoruz.',
  keywords: ['klima bayii', 'bursa klima', 'mhi yetkili', 'euroform bayii', 'klima montaj', 'klima servis'],
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://vedel.com.tr/hakkimizda',
    siteName: 'VEDEL Klima',
    title: 'Hakkımızda | VEDEL Klima',
    description: 'VEDEL Klima olarak 25 yılı aşkın süredir iklimlendirme sektöründe hizmet veriyoruz. MHI ve Euroform yetkili bayisi.',
    images: [
      {
        url: '/vedel-logo.png',
        width: 1200,
        height: 630,
        alt: 'VEDEL Klima - Hakkımızda',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Hakkımızda | VEDEL Klima',
    description: 'VEDEL Klima olarak 25 yılı aşkın süredir iklimlendirme sektöründe hizmet veriyoruz.',
    images: ['/vedel-logo.png'],
  },
}
import Link from 'next/link'
import {
  Phone,
  Clock,
  Award,
  Wrench,
  Shield,
  Leaf,
  Users,
  CheckCircle2,
  ArrowRight,
  Zap
} from 'lucide-react'

const stats = [
  { number: '20+', label: 'Yıl Tecrübe', icon: Clock },
  { number: '1000+', label: 'Tamamlanan Proje', icon: Award },
  { number: '7/24', label: 'Teknik Destek', icon: Phone },
  { number: '25+', label: 'Uzman Teknisyen', icon: Users },
]

const services = [
  {
    icon: Wrench,
    title: 'Projelendirme',
    description: 'İhtiyaçlarınıza özel iklimlendirme çözümlerinin tasarımı ve planlaması.'
  },
  {
    icon: Shield,
    title: 'Montaj & Devreye Alma',
    description: 'Profesional ekip ile güvenli kurulum ve sistemlerin devreye alınması.'
  },
  {
    icon: Zap,
    title: 'Periyodik Bakım',
    description: 'Sistemlerin verimli çalışması için düzenli bakım ve kontroller.'
  },
  {
    icon: Award,
    title: 'Arıza Müdahalesi',
    description: 'Hızlı ve etkili arıza çözümleri ile kesintisiz hizmet.'
  }
]

const partners = [
  { name: 'Mitsubishi Heavy Industries', logo: '/mhi-logo.png', desc: 'VRF, Split, Multi Sistemler' },
  { name: 'Euroform', logo: '/euroform.png', desc: 'Klima ve soğutma sistemleri' }
]

export default function Hakkimizda() {
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
            <h1 className="hero-title mb-4 text-3xl font-bold text-white sm:mb-6 sm:text-4xl md:text-6xl">
              Biz Kimiz?
            </h1>
            <p className="hero-subtitle mx-auto max-w-3xl text-base leading-relaxed text-red-100 sm:text-xl md:text-2xl">
              Vedel Klima olarak 25 yılı aşkın süredir iklimlendirme sektörünün içinde;
              yaşam alanlarından büyük ölçekli endüstriyel tesislere, ofis binalarından
              alışveriş merkezlerine kadar uzanan geniş bir yelpazede hizmet veriyoruz.
            </p>
          </div>

          <div className="mt-10 grid grid-cols-2 gap-3 sm:mt-16 sm:gap-4 md:grid-cols-4 md:gap-8">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="stat-card rounded-2xl border border-white/20 bg-white/10 p-4 text-center backdrop-blur-sm sm:p-6"
              >
                <stat.icon className="mx-auto mb-2 h-6 w-6 text-red-300 sm:mb-3 sm:h-8 sm:w-8" />
                <div className="mb-1 text-xl font-bold text-white sm:text-2xl md:text-4xl">{stat.number}</div>
                <div className="text-xs text-red-200 sm:text-sm md:text-base">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-12 sm:py-16 md:py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="grid items-center gap-8 md:grid-cols-2 md:gap-12">
            <div className="section-content">
              <h2 className="section-title mb-4 text-2xl font-bold text-gray-900 sm:mb-6 sm:text-3xl md:text-4xl">
                25 Yılı Aşkın Tecrübe ile Sizin Yanınızdayız
              </h2>
              <div className="space-y-4 text-sm leading-relaxed text-gray-600 sm:space-y-6 sm:text-base">
                <p>
                  Kuruluşumuzdan bu yana temel hedefimiz, müşterilerimize konforlu,
                  enerji verimli ve sürdürülebilir çözümler sunmak oldu.
                </p>
                <p>
                  Yıllar içinde edindiğimiz deneyimle; projelendirme aşamasından montaj
                  ve devreye alma süreçlerine, periyodik bakım ve arıza müdahalesi
                  hizmetlerine kadar eksiksiz bir portföy oluşturduk.
                </p>
                <p>
                  Zengin referans listemizde üretim tesisleri, kurumsal kampüsler,
                  butik oteller ve toplu konut projeleri yer alıyor. Her işimizde,
                  sektörün öncü markaları <strong>Mitsubishi Heavy Industries</strong> ve {' '}
                  <strong> Euroform&apos;un</strong> yenilikçi ürün gamını kullanarak maksimum verim hedefliyoruz.
                </p>
              </div>
            </div>
            <div className="section-content relative">
              <div className="rounded-3xl bg-gradient-to-br from-red-50 to-orange-50 p-5 sm:p-8">
                <div className="grid grid-cols-2 gap-3 sm:gap-4">
                  <div className="rounded-2xl bg-white p-4 text-center shadow-lg sm:p-6">
                    <Award className="mx-auto mb-2 h-10 w-10 text-red-600 sm:mb-3 sm:h-12 sm:w-12" />
                    <h3 className="text-sm font-bold text-gray-900 sm:text-base">Ödüllü Hizmet</h3>
                    <p className="mt-1 text-xs text-gray-500 sm:mt-2 sm:text-sm">Sektör lideri markalar</p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 text-center shadow-lg sm:p-6">
                    <Users className="mx-auto mb-2 h-10 w-10 text-red-600 sm:mb-3 sm:h-12 sm:w-12" />
                    <h3 className="text-sm font-bold text-gray-900 sm:text-base">Uzman Ekip</h3>
                    <p className="mt-1 text-xs text-gray-500 sm:mt-2 sm:text-sm">25+ teknisyen</p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 text-center shadow-lg sm:p-6">
                    <Shield className="mx-auto mb-2 h-10 w-10 text-red-600 sm:mb-3 sm:h-12 sm:w-12" />
                    <h3 className="text-sm font-bold text-gray-900 sm:text-base">Garantili İşçilik</h3>
                    <p className="mt-1 text-xs text-gray-500 sm:mt-2 sm:text-sm">Steril işlemler</p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 text-center shadow-lg sm:p-6">
                    <Clock className="mx-auto mb-2 h-10 w-10 text-red-600 sm:mb-3 sm:h-12 sm:w-12" />
                    <h3 className="text-sm font-bold text-gray-900 sm:text-base">Hızlı Servis</h3>
                    <p className="mt-1 text-xs text-gray-500 sm:mt-2 sm:text-sm">7/24 destek</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-12 sm:py-16 md:py-20 bg-white">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="mb-8 text-center sm:mb-12 md:mb-16">
            <h2 className="section-title mb-3 text-2xl font-bold text-gray-900 sm:mb-4 sm:text-3xl md:text-4xl">
              Kapsamlı Hizmetlerimiz
            </h2>
            <p className="section-content mx-auto max-w-2xl px-2 text-sm text-gray-600 sm:px-0 sm:text-base">
              Müşteri memnuniyetini daima odağımıza alarak, teknik ekibimizle 7/24
              destek hattı sunuyoruz.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-6 lg:grid-cols-4">
            {services.map((service, index) => (
              <div
                key={index}
                className="service-card group rounded-2xl border-2 border-gray-100 bg-white p-5 transition-all duration-300 sm:p-6 md:hover:border-red-200 md:hover:shadow-xl"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-red-100 transition-colors duration-300 sm:h-14 sm:w-14 md:group-hover:bg-red-600">
                  <service.icon className="h-6 w-6 text-red-600 transition-colors duration-300 sm:h-7 sm:w-7 md:group-hover:text-white" />
                </div>
                <h3 className="mb-2 text-lg font-bold text-gray-900 sm:mb-3 sm:text-xl">{service.title}</h3>
                <p className="text-sm leading-relaxed text-gray-600">{service.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-12 sm:py-16 md:py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="mb-8 text-center sm:mb-12 md:mb-16">
            <h2 className="section-title mb-3 text-2xl font-bold text-white sm:mb-4 sm:text-3xl md:text-4xl">
              İş Ortaklarımız
            </h2>
            <p className="section-content mx-auto max-w-2xl px-2 text-sm text-gray-400 sm:px-0 sm:text-base">
              Sektörün öncü markaları ile stratejik iş ortaklığı kurarak maksimum verim
              hedefliyoruz.
            </p>
          </div>

          <div className="mx-auto grid max-w-4xl grid-cols-1 gap-4 sm:gap-8 md:grid-cols-2">
            {partners.map((partner, index) => (
              <div
                key={index}
                className="partner-card flex flex-col items-center gap-4 rounded-2xl border border-white/10 bg-white/5 p-5 text-center backdrop-blur-sm transition-colors duration-300 active:bg-white/10 sm:flex-row sm:gap-6 sm:p-8 sm:text-left md:hover:bg-white/10"
              >
                <div className="flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-xl bg-white p-3 sm:h-24 sm:w-24 sm:p-4">
                  <Image
                    src={partner.logo}
                    alt={partner.name}
                    width={80}
                    height={80}
                    className="h-full w-full object-contain"
                  />
                </div>
                <div className="min-w-0">
                  <h3 className="mb-1 text-lg font-bold text-white sm:mb-2 sm:text-xl">{partner.name}</h3>
                  <p className="text-sm text-gray-400">{partner.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-12 sm:py-16 md:py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-red-600 to-red-700 p-5 sm:p-8 md:p-12">
            <div className="absolute right-0 top-0 h-40 w-40 -translate-y-1/2 translate-x-1/2 rounded-full bg-white/10 sm:h-64 sm:w-64" />
            <div className="absolute bottom-0 left-0 h-32 w-32 -translate-x-1/2 translate-y-1/2 rounded-full bg-white/10 sm:h-48 sm:w-48" />

            <div className="relative z-10 grid items-center gap-8 md:grid-cols-2 md:gap-12">
              <div>
                <h2 className="mb-3 text-2xl font-bold text-white sm:mb-4 sm:text-3xl md:text-4xl">
                  7/24 Teknik Destek
                </h2>
                <p className="mb-6 text-sm leading-relaxed text-red-100 sm:mb-8 sm:text-base md:text-lg">
                  Servis ağımız; alanında uzman teknisyenlerimiz, orijinal yedek parça
                  stoku ve profesyonel ekipmanlarımızla ülke geneline yayılmış durumda.
                  Bu sayede olası bir arıza veya bakım talebine en kısa sürede müdahale
                  ediyor, sistemlerinizin kesintisiz çalışmasını garanti ediyoruz.
                </p>
                <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:gap-4">
                  <div className="flex items-center gap-2 text-white">
                    <CheckCircle2 className="h-5 w-5 shrink-0" />
                    <span className="text-sm font-medium sm:text-base">Uzman Teknisyenler</span>
                  </div>
                  <div className="flex items-center gap-2 text-white">
                    <CheckCircle2 className="h-5 w-5 shrink-0" />
                    <span className="text-sm font-medium sm:text-base">Orijinal Yedek Parça</span>
                  </div>
                  <div className="flex items-center gap-2 text-white">
                    <CheckCircle2 className="h-5 w-5 shrink-0" />
                    <span className="text-sm font-medium sm:text-base">Hızlı Müdahale</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-col gap-3 sm:gap-4">
                <a
                  href="tel:+902244132316"
                  className="flex min-h-12 items-center justify-center gap-3 rounded-xl bg-white px-6 py-4 text-base font-bold text-red-600 transition-colors active:bg-gray-100 sm:text-lg md:hover:bg-gray-100"
                >
                  <Phone className="h-6 w-6 shrink-0" />
                  <span>(0224) 413 23 16</span>
                </a>
                <Link
                  href="/iletisim"
                  className="flex min-h-12 items-center justify-center gap-2 rounded-xl bg-red-800 px-6 py-4 text-base font-bold text-white transition-colors active:bg-red-900 sm:text-lg md:hover:bg-red-900"
                >
                  <span>İletişime Geç</span>
                  <ArrowRight className="h-5 w-5 shrink-0" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white py-12 sm:py-16 md:py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="grid items-center gap-8 md:grid-cols-2 md:gap-12">
            <div className="order-2 md:order-1">
              <div className="relative">
                <div className="rounded-3xl bg-gradient-to-br from-green-50 to-emerald-50 p-5 sm:p-8">
                  <div className="grid grid-cols-2 gap-4 sm:gap-6">
                    <div className="text-center">
                      <Leaf className="mx-auto mb-2 h-10 w-10 text-green-600 sm:mb-3 sm:h-12 sm:w-12" />
                      <h3 className="text-sm font-bold text-gray-900 sm:text-base">Sürdürülebilirlik</h3>
                      <p className="mt-1 text-xs text-gray-600 sm:mt-2 sm:text-sm">Düşük enerji tüketimli inverter teknolojileri</p>
                    </div>
                    <div className="text-center">
                      <Zap className="mx-auto mb-2 h-10 w-10 text-green-600 sm:mb-3 sm:h-12 sm:w-12" />
                      <h3 className="text-sm font-bold text-gray-900 sm:text-base">Enerji Verimliliği</h3>
                      <p className="mt-1 text-xs text-gray-600 sm:mt-2 sm:text-sm">Maksimum performans, minimum sarfiyat</p>
                    </div>
                    <div className="text-center">
                      <Shield className="mx-auto mb-2 h-10 w-10 text-green-600 sm:mb-3 sm:h-12 sm:w-12" />
                      <h3 className="text-sm font-bold text-gray-900 sm:text-base">Hava Kalitesi</h3>
                      <p className="mt-1 text-xs text-gray-600 sm:mt-2 sm:text-sm">HEPA filtreli sistemler</p>
                    </div>
                    <div className="text-center">
                      <Users className="mx-auto mb-2 h-10 w-10 text-green-600 sm:mb-3 sm:h-12 sm:w-12" />
                      <h3 className="text-sm font-bold text-gray-900 sm:text-base">Eğitimli Kadro</h3>
                      <p className="mt-1 text-xs text-gray-600 sm:mt-2 sm:text-sm">Düzenli teknik eğitimler</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="order-1 md:order-2">
              <h2 className="section-title mb-4 text-2xl font-bold text-gray-900 sm:mb-6 sm:text-3xl md:text-4xl">
                Sürdürülebilir Geleceğe Katkı
              </h2>
              <div className="space-y-4 text-sm leading-relaxed text-gray-600 sm:space-y-6 sm:text-base">
                <p>
                  Sürdürülebilirlik ilkesiyle; düşük enerji tüketimli inverter
                  teknolojilerine önem veriyor, iç ortam havası kalitesini artıracak
                  HEPA filtreli sistemleri öneriyoruz.
                </p>
                <p>
                  Ar-Ge ortaklıklarıyla sürekli güncel kalıyor, çalışanlarımızın
                  düzenli eğitimlerle en son teknik bilgi ve iş güvenliği standartlarına
                  hakim olmasını sağlıyoruz.
                </p>
                <p className="text-base font-medium text-gray-900 sm:text-lg">
                  Vedel Klima, yarım asrı geçen tecrübesi ve müşteri odaklı hizmet
                  anlayışıyla, her büyüklükteki projeye çözüm ortağı olmaya devam ediyor.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
