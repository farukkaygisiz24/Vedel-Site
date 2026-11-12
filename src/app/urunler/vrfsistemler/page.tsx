import type { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, ArrowUpRight } from 'lucide-react'

export const metadata: Metadata = {
  title: 'VRF Sistemler | 2V Klima & MHI',
  description:
    'VRF (Variable Refrigerant Flow) sistemler. Mitsubishi Heavy Industries VRF çözümleri. Projelendirme, satış, montaj ve servis: 2V Klima.',
  keywords: [
    'vrf klima',
    'vrf sistem',
    '2v klima',
    'mhi vrf',
    'mitsubishi vrf',
    'merkezi klima',
    'büyük bina klima',
    'değişken soğutucu akışkan',
  ],
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: 'https://vedel.com.tr/urunler/vrfsistemler',
    siteName: 'VEDEL Klima',
    title: 'VRF Sistemler | VEDEL Klima & 2V Klima',
    description:
      'Büyük bina ve tesisler için MHI VRF sistemleri. Proje ve ürün detayları için 2V Klima.',
    images: [
      {
        url: '/2vklima-logo.png',
        width: 1200,
        height: 630,
        alt: '2V Klima VRF Sistemler',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VRF Sistemler | VEDEL Klima & 2V Klima',
    description: 'MHI VRF sistemleri. Proje ve ürün detayları için 2V Klima.',
    images: ['/2vklima-logo.png'],
  },
}

const VRF_POINTS = [
  {
    title: 'Değişken kapasite',
    text: 'Sistem, anlık soğutma ve ısıtma ihtiyacına göre soğutucu akışkan debisini ayarlar. Gereksiz enerji tüketimini azaltır.',
  },
  {
    title: 'Bağımsız oda kontrolü',
    text: 'Tek dış üniteye bağlı iç üniteler ayrı ayrı yönetilir. Ofis, otel ve AVM gibi çok bölgeli yapılarda esneklik sağlar.',
  },
  {
    title: 'Yüksek enerji verimi',
    text: 'Geleneksel merkezi sistemlere kıyasla önemli ölçüde daha verimli çalışır; işletme maliyetini uzun vadede düşürür.',
  },
  {
    title: 'Ölçeklenebilir yapı',
    text: 'Küçük ticari projelerden büyük komplekslere kadar kapasite ihtiyaca göre planlanır ve genişletilebilir.',
  },
] as const

const USE_CASES = [
  {
    title: 'Ofis ve iş merkezleri',
    text: 'Kat ve oda bazlı sıcaklık yönetimi, merkezi kontrol ve düşük işletme maliyeti.',
  },
  {
    title: 'Otel ve konaklama',
    text: 'Misafir odalarında bağımsız konfor; ortak alanlarda dengeli iklimlendirme.',
  },
  {
    title: 'AVM ve perakende',
    text: 'Geniş hacimler, yoğun kullanım ve sürekli açık alanlar için yüksek kapasite.',
  },
  {
    title: 'Üretim ve tesis',
    text: 'Endüstriyel ve karma kullanımlı yapılarda güvenilir, uzun ömürlü merkezi çözüm.',
  },
] as const

const TWO_V_SERVICES = [
  {
    title: 'VRF sistemleri',
    text: 'MHI ürün gamıyla projelendirme, satış ve uygulama.',
  },
  {
    title: 'Projelendirme',
    text: 'Keşif, kapasite hesabı ve mekâna uygun mühendislik.',
  },
  {
    title: 'Bakım & servis',
    text: 'Yetkili servis standartlarında periyodik bakım ve onarım.',
  },
] as const

export default function VRFSistemlerPage() {
  return (
    <main className="min-h-screen bg-white">
      {/* Hero */}
      <section className="border-b border-neutral-200/80 bg-[#f5f4f1]">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-16 sm:px-6 sm:py-20 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)] lg:items-end lg:gap-14 lg:px-8 lg:py-24">
          <div>
            <p className="mb-3 text-sm font-semibold tracking-[0.2em] text-red-600">
              VRF SİSTEMLER
            </p>
            <h1 className="mb-5 text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl lg:text-5xl lg:leading-[1.1]">
              Büyük yapılar için merkezi, verimli iklimlendirme.
            </h1>
            <p className="max-w-xl text-base leading-relaxed text-neutral-600 sm:text-lg">
              VRF (Variable Refrigerant Flow), tek dış üniteye bağlı çoklu iç
              ünitelerle bölgesel kontrol sunan gelişmiş merkezi sistemdir. VRF
              markamız{' '}
              <strong className="font-semibold text-neutral-800">2V Klima</strong>
              ; proje, ürün ve teklif süreçleri 2vklima.com üzerinden yürür.
              Split, multi ve profesyonel sistemler için Vedel Klima yanınızda.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <a
                href="https://www.2vklima.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-md bg-red-600 px-6 py-3.5 text-sm font-bold text-white transition-colors hover:bg-red-700"
              >
                2vklima.com
                <ArrowUpRight className="h-4 w-4" />
              </a>
              <Link
                href="/iletisim"
                className="inline-flex items-center gap-2 rounded-md border border-neutral-300 bg-white px-6 py-3.5 text-sm font-semibold text-neutral-800 transition-colors hover:border-neutral-400"
              >
                Vedel iletişim
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>

          <div className="rounded-sm border border-neutral-200 bg-white p-6 sm:p-8">
            <p className="mb-4 text-xs font-semibold tracking-[0.18em] text-red-600 uppercase">
              VRF markamız
            </p>
            <div className="relative mb-5 h-14 w-full max-w-[240px]">
              <Image
                src="/2vklima-logo.png"
                alt="2V Klima"
                fill
                className="object-contain object-left"
                sizes="240px"
                priority
              />
            </div>
            <p className="mb-4 text-sm leading-relaxed text-neutral-600">
              Mitsubishi Heavy Industries yetkili servisi. VRF projelendirme,
              satış, montaj, bakım ve onarımda uzman ekibimiz.
            </p>
            <div className="flex items-center gap-4 border-t border-neutral-100 pt-4">
              <div className="relative h-10 w-10 shrink-0 overflow-hidden rounded-md border border-neutral-100 bg-white">
                <Image
                  src="/2v-mark.png"
                  alt=""
                  fill
                  className="object-contain p-1"
                  sizes="40px"
                />
              </div>
              <div className="min-w-0 text-sm">
                <p className="font-semibold text-neutral-900">2vklima.com</p>
                <p className="text-neutral-500">VRF ürün ve proje sitemiz</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* VRF nedir */}
      <section className="border-b border-neutral-200/80 bg-white py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-10 max-w-2xl lg:mb-12">
            <p className="mb-3 text-sm font-semibold tracking-[0.2em] text-red-600">
              TEKNOLOJİ
            </p>
            <h2 className="mb-4 text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
              VRF sistemi nedir?
            </h2>
            <p className="text-base leading-relaxed text-neutral-600">
              Değişken soğutucu akışkan debili sistemler, merkezi iklimlendirmenin
              gelişmiş biçimidir. İhtiyaca göre kapasite ayarlanır; her iç ünite
              bağımsız yönetilebilir. Ofis, otel, AVM ve tesis ölçeğinde tercih
              edilir.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:gap-12">
            {VRF_POINTS.map((item) => (
              <article
                key={item.title}
                className="border-t-2 border-neutral-900 pt-5 transition-colors hover:border-red-600"
              >
                <h3 className="mb-2 text-lg font-bold text-neutral-900">{item.title}</h3>
                <p className="text-sm leading-relaxed text-neutral-600 sm:text-[15px]">
                  {item.text}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* 2V spotlight */}
      <section className="border-b border-neutral-200/80 bg-[#f5f4f1] py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:items-center lg:gap-16">
            <div>
              <p className="mb-3 text-sm font-semibold tracking-[0.2em] text-red-600">
                2V KLİMA
              </p>
              <h2 className="mb-5 text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
                VRF&apos;de markamız: 2V Klima.
              </h2>
              <p className="mb-4 text-base leading-relaxed text-neutral-600">
                Vedel Klima konut ve ticari split, multi ve profesyonel
                sistemlerde hizmet verirken; VRF ve büyük ölçekli merkezi
                iklimlendirme işimizi 2V Klima çatısı altında yürütüyoruz. Aynı
                ekip, VRF&apos;ye özel odak.
              </p>
              <p className="mb-8 text-base leading-relaxed text-neutral-600">
                Keşiften montaja, periyodik bakımdan onarıma kadar MHI yetkili
                servis standartlarıyla ilerliyoruz. Ürün gamı, referanslar ve
                teklif talebi için 2vklima.com ana sitemizdir.
              </p>
              <a
                href="https://www.2vklima.com"
                target="_blank"
                rel="noopener noreferrer"
                className="group inline-flex items-center justify-between gap-4 border-t border-neutral-300 pt-5 transition-colors hover:border-red-600"
              >
                <span>
                  <span className="block text-sm font-bold text-neutral-900 transition-colors group-hover:text-red-600">
                    2vklima.com&apos;u ziyaret edin
                  </span>
                  <span className="mt-0.5 block text-sm text-neutral-500">
                    VRF sistemleri, referanslar ve teklif
                  </span>
                </span>
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-neutral-300 text-neutral-700 transition-colors group-hover:border-red-600 group-hover:bg-red-600 group-hover:text-white">
                  <ArrowUpRight className="h-4 w-4" />
                </span>
              </a>
            </div>

            <div className="border-y border-neutral-300/80">
              {TWO_V_SERVICES.map((item, index) => (
                <div
                  key={item.title}
                  className="grid grid-cols-[auto_minmax(0,1fr)] gap-4 border-b border-neutral-300/80 py-5 last:border-b-0 sm:gap-5 sm:py-6"
                >
                  <span className="font-display pt-0.5 text-2xl leading-none text-red-600 sm:text-3xl">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  <div>
                    <h3 className="mb-1 text-base font-bold text-neutral-900 sm:text-lg">
                      {item.title}
                    </h3>
                    <p className="text-sm leading-relaxed text-neutral-600">
                      {item.text}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Kullanım alanları */}
      <section className="border-b border-neutral-200/80 bg-white py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto mb-10 max-w-2xl text-center lg:mb-12">
            <p className="mb-3 text-sm font-semibold tracking-[0.2em] text-red-600">
              UYGULAMA
            </p>
            <h2 className="mb-4 text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
              Nerede tercih edilir?
            </h2>
            <p className="text-base leading-relaxed text-neutral-600">
              Çok bölgeli, yüksek kapasite gerektiren yapılarda VRF hem konfor
              hem işletme verimi sağlar.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-px overflow-hidden rounded-sm bg-neutral-300/70 sm:grid-cols-2">
            {USE_CASES.map((item) => (
              <div
                key={item.title}
                className="bg-white p-5 sm:p-6"
              >
                <h3 className="mb-2 text-base font-bold text-neutral-900 sm:text-lg">
                  {item.title}
                </h3>
                <p className="text-sm leading-relaxed text-neutral-600">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* MHI */}
      <section className="border-b border-neutral-200/80 bg-[#f5f4f1] py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid items-center gap-10 lg:grid-cols-[auto_minmax(0,1fr)] lg:gap-14">
            <div className="relative mx-auto h-16 w-48 lg:mx-0 lg:h-20 lg:w-56">
              <Image
                src="/mhi-logo.png"
                alt="Mitsubishi Heavy Industries"
                fill
                className="object-contain object-left"
                sizes="224px"
              />
            </div>
            <div>
              <p className="mb-2 text-sm font-semibold tracking-[0.2em] text-red-600">
                MITSUBISHI HEAVY INDUSTRIES
              </p>
              <h2 className="mb-3 text-2xl font-bold tracking-tight text-neutral-900 sm:text-3xl">
                Japon mühendisliği, VRF&apos;de kanıtlanmış güvenilirlik.
              </h2>
              <p className="max-w-2xl text-base leading-relaxed text-neutral-600">
                2V Klima olarak Mitsubishi Heavy Industries yetkili servisiyiz;
                orijinal ürün ve yedek parça güvencesiyle çalışıyoruz. Enerji
                verimli inverter teknolojisi, uzun ömür ve zorlu koşullarda
                dayanıklılık VRF projelerimizin temelidir.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-neutral-950 py-14 sm:py-16">
        <div className="mx-auto flex max-w-7xl flex-col gap-8 px-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div className="max-w-xl">
            <h2 className="mb-3 text-2xl font-bold text-white sm:text-3xl">
              VRF projeniz için doğru adres.
            </h2>
            <p className="text-sm leading-relaxed text-neutral-400 sm:text-base">
              VRF ürün ve teklif için 2vklima.com; split, multi ve profesyonel
              sistemler için Vedel Klima. İhtiyacınıza göre doğru kanaldan
              ilerlersiniz.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <a
              href="https://www.2vklima.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-md bg-red-600 px-6 py-3.5 text-sm font-bold text-white transition-colors hover:bg-red-700"
            >
              2vklima.com
              <ArrowUpRight className="h-4 w-4" />
            </a>
            <a
              href="tel:+905444578576"
              className="inline-flex items-center gap-2 rounded-md border border-neutral-700 px-6 py-3.5 text-sm font-semibold text-white transition-colors hover:border-neutral-500"
            >
              (0544) 457 85 76
            </a>
            <Link
              href="/iletisim"
              className="inline-flex items-center gap-2 rounded-md border border-neutral-700 px-6 py-3.5 text-sm font-semibold text-neutral-300 transition-colors hover:border-neutral-500 hover:text-white"
            >
              Vedel iletişim
            </Link>
          </div>
        </div>
      </section>
    </main>
  )
}
