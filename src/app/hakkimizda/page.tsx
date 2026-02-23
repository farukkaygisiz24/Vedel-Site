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
  MapPin,
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
  { number: '25+', label: 'Yıl Tecrübe', icon: Clock },
  { number: '1000+', label: 'Tamamlanan Proje', icon: Award },
  { number: '7/24', label: 'Teknik Destek', icon: Phone },
  { number: '50+', label: 'Uzman Teknisyen', icon: Users },
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

      <section className="relative pt-20 pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-red-900 via-red-800 to-red-900" />
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-20 w-96 h-96 bg-red-400 rounded-full blur-3xl" />
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="hero-title text-4xl md:text-6xl font-bold text-white mb-6">
              Biz Kimiz?
            </h1>
            <p className="hero-subtitle text-xl md:text-2xl text-red-100 leading-relaxed max-w-3xl mx-auto">
              Vedel Klima olarak 25 yılı aşkın süredir iklimlendirme sektörünün içinde;
              yaşam alanlarından büyük ölçekli endüstriyel tesislere, ofis binalarından
              alışveriş merkezlerine kadar uzanan geniş bir yelpazede hizmet veriyoruz.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8 mt-16">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="stat-card bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center border border-white/20"
              >
                <stat.icon className="w-8 h-8 text-red-300 mx-auto mb-3" />
                <div className="text-2xl md:text-4xl font-bold text-white mb-1">{stat.number}</div>
                <div className="text-red-200 text-sm md:text-base">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="section-content">
              <h2 className="section-title text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                25 Yılı Aşkın Tecrübe ile Sizin Yanınızdayız
              </h2>
              <div className="space-y-6 text-gray-600 leading-relaxed">
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
              <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-3xl p-8">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white rounded-2xl p-6 shadow-lg text-center">
                    <Award className="w-12 h-12 text-red-600 mx-auto mb-3" />
                    <h3 className="font-bold text-gray-900">Ödüllü Hizmet</h3>
                    <p className="text-sm text-gray-500 mt-2">Sektör lideri markalar</p>
                  </div>
                  <div className="bg-white rounded-2xl p-6 shadow-lg text-center">
                    <Users className="w-12 h-12 text-red-600 mx-auto mb-3" />
                    <h3 className="font-bold text-gray-900">Uzman Ekip</h3>
                    <p className="text-sm text-gray-500 mt-2">50+ teknisyen</p>
                  </div>
                  <div className="bg-white rounded-2xl p-6 shadow-lg text-center">
                    <Shield className="w-12 h-12 text-red-600 mx-auto mb-3" />
                    <h3 className="font-bold text-gray-900">Garantili İşçilik</h3>
                    <p className="text-sm text-gray-500 mt-2">Steril işlemler</p>
                  </div>
                  <div className="bg-white rounded-2xl p-6 shadow-lg text-center">
                    <Clock className="w-12 h-12 text-red-600 mx-auto mb-3" />
                    <h3 className="font-bold text-gray-900">Hızlı Servis</h3>
                    <p className="text-sm text-gray-500 mt-2">7/24 destek</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="section-title text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Kapsamlı Hizmetlerimiz
            </h2>
            <p className="section-content text-gray-600 max-w-2xl mx-auto">
              Müşteri memnuniyetini daima odağımıza alarak, teknik ekibimizle 7/24
              destek hattı sunuyoruz.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {services.map((service, index) => (
              <div
                key={index}
                className="service-card group bg-white border-2 border-gray-100 rounded-2xl p-6 hover:border-red-200 hover:shadow-xl transition-all duration-300"
              >
                <div className="w-14 h-14 bg-red-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-red-600 transition-colors duration-300">
                  <service.icon className="w-7 h-7 text-red-600 group-hover:text-white transition-colors duration-300" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{service.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{service.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="section-title text-3xl md:text-4xl font-bold text-white mb-4">
              İş Ortaklarımız
            </h2>
            <p className="section-content text-gray-400 max-w-2xl mx-auto">
              Sektörün öncü markaları ile stratejik iş ortaklığı kurarak maksimum verim
              hedefliyoruz.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {partners.map((partner, index) => (
              <div
                key={index}
                className="partner-card bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 flex flex-col sm:flex-row items-center gap-6 hover:bg-white/10 transition-colors duration-300 text-center sm:text-left"
              >
                <div className="w-24 h-24 bg-white rounded-xl p-4 flex-shrink-0">
                  <Image
                    src={partner.logo}
                    alt={partner.name}
                    width={80}
                    height={80}
                    className="w-full h-full object-contain"
                  />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">{partner.name}</h3>
                  <p className="text-gray-400 text-sm">{partner.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="bg-gradient-to-r from-red-600 to-red-700 rounded-3xl p-8 md:p-12 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2" />

            <div className="relative z-10 grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                  7/24 Teknik Destek
                </h2>
                <p className="text-red-100 text-lg leading-relaxed mb-8">
                  Servis ağımız; alanında uzman teknisyenlerimiz, orijinal yedek parça
                  stoku ve profesyonel ekipmanlarımızla ülke geneline yayılmış durumda.
                  Bu sayede olası bir arıza veya bakım talebine en kısa sürede müdahale
                  ediyor, sistemlerinizin kesintisiz çalışmasını garanti ediyoruz.
                </p>
                <div className="flex flex-wrap gap-4">
                  <div className="flex items-center gap-2 text-white">
                    <CheckCircle2 className="w-5 h-5" />
                    <span className="font-medium">Uzman Teknisyenler</span>
                  </div>
                  <div className="flex items-center gap-2 text-white">
                    <CheckCircle2 className="w-5 h-5" />
                    <span className="font-medium">Orijinal Yedek Parça</span>
                  </div>
                  <div className="flex items-center gap-2 text-white">
                    <CheckCircle2 className="w-5 h-5" />
                    <span className="font-medium">Hızlı Müdahale</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-col gap-4">
                <a
                  href="tel:+902244131617"
                  className="flex items-center justify-center gap-3 bg-white text-red-600 font-bold py-4 px-8 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  <Phone className="w-6 h-6" />
                  <span>(0224) 413 16 17</span>
                </a>
                <Link
                  href="/iletisim"
                  className="flex items-center justify-center gap-2 bg-red-800 text-white font-bold py-4 px-8 rounded-xl hover:bg-red-900 transition-colors"
                >
                  <span>İletişime Geç</span>
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1">
              <div className="relative">
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-3xl p-8">
                  <div className="grid grid-cols-2 gap-6">
                    <div className="text-center">
                      <Leaf className="w-12 h-12 text-green-600 mx-auto mb-3" />
                      <h3 className="font-bold text-gray-900">Sürdürülebilirlik</h3>
                      <p className="text-sm text-gray-600 mt-2">Düşük enerji tüketimli inverter teknolojileri</p>
                    </div>
                    <div className="text-center">
                      <Zap className="w-12 h-12 text-green-600 mx-auto mb-3" />
                      <h3 className="font-bold text-gray-900">Enerji Verimliliği</h3>
                      <p className="text-sm text-gray-600 mt-2">Maksimum performans, minimum sarfiyat</p>
                    </div>
                    <div className="text-center">
                      <Shield className="w-12 h-12 text-green-600 mx-auto mb-3" />
                      <h3 className="font-bold text-gray-900">Hava Kalitesi</h3>
                      <p className="text-sm text-gray-600 mt-2">HEPA filtreli sistemler</p>
                    </div>
                    <div className="text-center">
                      <Users className="w-12 h-12 text-green-600 mx-auto mb-3" />
                      <h3 className="font-bold text-gray-900">Eğitimli Kadro</h3>
                      <p className="text-sm text-gray-600 mt-2">Düzenli teknik eğitimler</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="order-1 md:order-2">
              <h2 className="section-title text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Sürdürülebilir Geleceğe Katkı
              </h2>
              <div className="space-y-6 text-gray-600 leading-relaxed">
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
                <p className="text-lg font-medium text-gray-900">
                  Vedel Klima, yarım asrı geçen tecrübesi ve müşteri odaklı hizmet
                  anlayışıyla, her büyüklükteki projeye çözüm ortağı olmaya devam ediyor.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4 text-center">
          <h2 className="section-title text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            İhtiyaçlarınızı Dinlemek İçin Buradayız
          </h2>
          <p className="section-content text-gray-600 max-w-2xl mx-auto mb-8">
            Size özel en uygun teklif ve teknik desteği sağlamak için her zaman yanınızdayız.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/klimani-sec"
              className="inline-flex items-center justify-center gap-2 bg-red-600 text-white font-bold py-4 px-8 rounded-xl hover:bg-red-700 transition-colors"
            >
              <span>Klimanı Seç</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/iletisim"
              className="inline-flex items-center justify-center gap-2 bg-white text-gray-900 font-bold py-4 px-8 rounded-xl border-2 border-gray-200 hover:border-red-600 hover:text-red-600 transition-colors"
            >
              <MapPin className="w-5 h-5" />
              <span>İletişim</span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
